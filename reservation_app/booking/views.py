from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import BookingForm, RegisterForm, LoginForm, CustomUserRegistrationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import Room, Hotel, Booking
from datetime import datetime, timedelta, date

@login_required
def profile_view(request):
    profile = request.user
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserRegistrationForm(instance=profile)
    return render(request, 'profile.html', {'form': form})

def home(request):
    return render(request, 'home.html')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('room_list')
    else:
        form = CustomUserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('room_list')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы вошли в систему!')
            return redirect('room_list')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
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
    tomorrow = today + timedelta(days=1)

    check_in = request.GET.get("check_in", today.strftime('%Y-%m-%d'))
    check_out = request.GET.get("check_out", tomorrow.strftime('%Y-%m-%d'))

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
