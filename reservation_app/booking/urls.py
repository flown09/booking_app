from django.urls import path
from .views import room_list, room_detail, hotel_detail, register_view, login_view, logout_view, my_bookings, hotel_list, profile_view

urlpatterns = [
    path('hotels/', hotel_list, name='hotel_list'),
    path('', room_list, name='room_list'),
    path('rooms/<int:pk>/', room_detail, name='room_detail'),
    path('hotels/<int:pk>/', hotel_detail, name='hotel_detail'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('my-bookings/', my_bookings, name='my_bookings'),
    path('profile/', profile_view, name='profile'),
]