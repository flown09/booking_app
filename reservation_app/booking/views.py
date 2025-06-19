import json
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import BookingForm, RegisterForm, LoginForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import Room, Hotel, Booking, CustomUser
from datetime import datetime, timedelta, date
import random


@require_POST
@login_required
def cancel_booking_view(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
        if booking.status != 'cancelled':
            booking.status = 'cancelled'
            booking.save()

            subject = 'Отмена бронирования'
            check_in_formatted = booking.check_in.strftime("%d.%m.%Y")
            check_out_formatted = booking.check_out.strftime("%d.%m.%Y")
            message = (
                f'Здравствуйте, вы отменили бронирование:\n'
                f'Отель: {booking.room.hotel.name}\n'
                f'Номер: {booking.room.name}\n'
                f'Период: с {check_in_formatted} по {check_out_formatted}\n'
            )
            recipient = [request.user.email]

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)

            return JsonResponse({'cancelled': True})
        else:
            return JsonResponse({'cancelled': False, 'error': 'already cancelled'})
    except Booking.DoesNotExist:
        return JsonResponse({'cancelled': False, 'error': 'not found'})

@csrf_exempt
@login_required
def update_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        if not email:
            return JsonResponse({'success': False, 'errors': 'Email не указан'})

        if CustomUser.objects.exclude(id=request.user.id).filter(email=email).exists():
            return JsonResponse({'success': False, 'errors': 'Email уже используется'})

        user = request.user
        user.save()

        code = str(random.randint(100000, 999999))

        send_mail(
            'Подтверждение email',
            f'Ваш код подтверждения: {code}',
            'noreply@example.com',
            [email],
        )

        request.session['pending_email'] = email
        request.session['email_code'] = code

        return JsonResponse({'success': True})


@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.cleaned_data.pop('email', None)
            for field in ['first_name', 'last_name', 'phone_number']:
                setattr(user, field, form.cleaned_data.get(field))
            user.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'profile.html', {'form': form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})

@csrf_exempt
def confirm_code_for_register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        input_code = data.get('code')
        session_code = request.session.get('email_code')
        user_data = request.session.get('pending_user_data')

        print(f"input_code: {input_code}, session_code: {session_code}")
        if str(input_code) == str(session_code) and user_data:
            user = CustomUser(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                username=user_data['email'].split('@')[0],
                is_active=True,
            )
            user.set_password(user_data['password'])
            user.save()

            login(request, user)

            del request.session['pending_user_data']
            del request.session['email_code']

            return JsonResponse({'confirmed': True})
        else:
            return JsonResponse({'confirmed': False})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user_data = {
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'password': form.cleaned_data['password1'],
            }
            request.session['pending_user_data'] = user_data

            code = str(random.randint(100000, 999999))

            send_mail(
                'Код подтверждения',
                f'Ваш код подтверждения: {code}',
                'noreply@example.com',
                [user_data['email']],
            )

            request.session['email_code'] = code

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
        session_code = request.session.get('email_code')
        pending_email = request.session.get('pending_email')

        if code == session_code and pending_email:
            user = request.user
            user.email = pending_email
            user.username = pending_email.split('@')[0]
            user.is_active = True
            user.save()

            del request.session['email_code']
            del request.session['pending_email']

            return JsonResponse({'confirmed': True})

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

    today = date.today()

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
            rooms = Room.objects.none()

    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

            if check_in_date >= check_out_date or check_in_date < today or check_out_date - check_in_date > timedelta(days=30):
                rooms = Room.objects.none()
            else:
                rooms = rooms.exclude(
                    booking__status__in=['pending', 'confirmed'],
                    booking__check_in__lt=check_out_date,
                    booking__check_out__gt=check_in_date
                ).distinct()

        except ValueError:
            rooms = Room.objects.none()

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
        messages.error(request, "Неверный формат даты.")
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
                subject = 'Подтверждение бронирования'

                message = (
                    f'Здравствуйте, {request.user.first_name or request.user.username}!\n\n'
                    f'Вы успешно отправили заявку на бронирование номера:\n'
                    f'Отель: {room.hotel.name}\n'
                    f'Номер: {room.name}\n'
                    f'Период: с {booking.check_in} по {booking.check_out}\n'
                    f'Адрес: {room.hotel.address}\n'
                    'Ожидайте подтверждения от администрации.\n\n'
                    'Спасибо, что выбрали наш сервис!'
                )
                recipient = [request.user.email]

                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)

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
