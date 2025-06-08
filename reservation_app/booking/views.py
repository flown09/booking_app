import json

from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import BookingForm, RegisterForm, LoginForm, CustomUserRegistrationForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import Room, Hotel, Booking, EmailConfirmation, CustomUser
from datetime import datetime, timedelta, date
import random

@csrf_exempt
@login_required
def update_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        if not email:
            return JsonResponse({'success': False, 'errors': 'Email не указан'})

        # Проверка уникальности email
        if CustomUser.objects.exclude(id=request.user.id).filter(email=email).exists():
            return JsonResponse({'success': False, 'errors': 'Email уже используется'})

        user = request.user
        user.email = email
        user.username = email.split('@')[0]
        user.is_active = False
        user.save()

        # Генерация и отправка кода
        code = str(random.randint(100000, 999999))
        EmailConfirmation.objects.update_or_create(
            user=user,
            defaults={'code': code, 'confirmed': False}
        )

        send_mail(
            'Подтверждение email',
            f'Ваш код подтверждения: {code}',
            'noreply@example.com',
            [email],
        )

        return JsonResponse({'success': True})


@login_required
def profile_view(request):
    user = request.user
    #confirmation = EmailConfirmation.objects.filter(user=user).first()

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'profile.html', {'form': form})

@login_required
def send_confirmation_code(request):
    code = str(random.randint(100000, 999999))
    EmailConfirmation.objects.update_or_create(
        user=request.user,
        defaults={'code': code, 'confirmed': False}
    )
    send_mail(
        'Код подтверждения почты',
        f'Ваш код подтверждения: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=False
    )
    return redirect('profile')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if '@' in user.email:
                user.username = user.email.split('@')[0]
            else:
                user.username = user.email
            user.is_active = False  # временно отключаем пользователя
            user.save()

            # Генерация кода
            code = str(random.randint(100000, 999999))
            EmailConfirmation.objects.create(user=user, code=code)

            # Отправка письма
            send_mail(
                'Код подтверждения',
                f'Ваш код подтверждения: {code}',
                'noreply@example.com',
                [user.email],
            )

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})

@csrf_exempt
def confirm_code_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code')
        confirmation = EmailConfirmation.objects.filter(code=code, confirmed=False).first()

        if confirmation:
            confirmation.confirmed = True
            confirmation.save()
            user = confirmation.user
            user.is_active = True
            user.save()
            login(request, user)
            return JsonResponse({'confirmed': True})
        else:
            return JsonResponse({'confirmed': False})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('room_list')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        try:
            user_obj = CustomUser.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('room_list')
        except CustomUser.DoesNotExist:
            pass

        form.add_error(None, 'Неверный email или пароль')

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

def hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'hotel_list.html', {'hotels': hotels})

def room_list(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    city = request.GET.get('city')
    hotel_name = request.GET.get('hotel')
    guests = request.GET.get('guests')

    # today = date.today()
    # tomorrow = today + timedelta(days=1)
    #
    # check_in = request.GET.get("check_in", today.strftime('%Y-%m-%d'))
    # check_out = request.GET.get("check_out", tomorrow.strftime('%Y-%m-%d'))

    rooms = Room.objects.filter(is_available=True)

    if city:
        rooms = rooms.filter(hotel__city__icontains=city)

    if hotel_name:
        rooms = rooms.filter(hotel__name__icontains=hotel_name)

    if guests:
        try:
            guests_int = int(guests)
            rooms = rooms.filter(capacity__gte=guests_int)
        except ValueError:
            pass

    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

            rooms = rooms.exclude(
                booking__check_in__lt=check_out_date,
                booking__check_out__gt=check_in_date
            ).distinct()

        except ValueError:
            pass

    return render(request, 'room_list.html', {
        'rooms': rooms,
        'check_in': check_in,
        'check_out': check_out,
        'city': city,
        'hotel': hotel_name,
        'guests': guests,
    })


def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    check_in_display = None
    check_out_display = None
    try:
        if check_in:
            check_in_display = datetime.strptime(check_in, "%Y-%m-%d").strftime("%d %B %Y")
        if check_out:
            check_out_display = datetime.strptime(check_out, "%Y-%m-%d").strftime("%d %B %Y")
    except ValueError:
        pass
    check_in = check_in_display
    check_out = check_out_display
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.room = room
                booking.user = request.user
                booking.status = 'pending'
                booking.save()
                messages.success(request, 'Бронирование успешно отправлено! Ожидайте подтверждения.')
                return redirect('room_detail', pk=room.pk)
        else:
            messages.warning(request, 'Необходимо войти в аккаунт для бронирования.')
            return redirect('login')
    else:
        form = BookingForm(initial={
            'check_in': check_in,
            'check_out': check_out,
        })

    return render(request, 'room_detail.html', {
        'room': room,
        'form': form,
        'check_in': check_in,
        'check_out': check_out,
    })

def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    return render(request, 'hotel_detail.html', {'hotel': hotel})
