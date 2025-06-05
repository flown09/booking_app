from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import BookingForm, RegisterForm, LoginForm, CustomUserRegistrationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import Room, Hotel, Booking
from datetime import datetime

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

    all_rooms = Room.objects.filter(is_available=True)
    rooms = []

    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

            for room in all_rooms:
                if room.is_available_for_dates(check_in_date, check_out_date):
                    rooms.append(room)
        except ValueError:
            # Неверный формат даты — можно обработать или проигнорировать
            pass
    else:
        # Если даты не указаны, показываем все доступные
        rooms = list(all_rooms)

    return render(request, 'room_list.html', {
        'rooms': rooms,
        'check_in': check_in,
        'check_out': check_out,
    })

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    form = BookingForm()

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

    return render(request, 'room_detail.html', {
        'room': room,
        'form': form,
    })

def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    return render(request, 'hotel_detail.html', {'hotel': hotel})
