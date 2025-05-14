from django.shortcuts import render, get_object_or_404, redirect
from .forms import BookingForm, RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import Room, Hotel

def register_view(request):
    if request.user.is_authenticated:
        return redirect('room_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('room_list')
    else:
        form = RegisterForm()

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

def room_list(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'room_list.html', {'rooms': rooms})

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
