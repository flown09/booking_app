from django.urls import path
from .views import (room_list, room_detail, hotel_detail, register_view, login_view, logout_view, my_bookings,
                    hotel_list, profile_view, confirm_code_view, confirm_code_for_register_view,
                    update_email, cancel_booking_view)

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
    path('confirm-code/', confirm_code_view, name='confirm_code'),
    path('confirm-code-for-register/', confirm_code_for_register_view, name='confirm_code_for_register'),
    path('update-email/', update_email, name='update_email'),
    path('cancel-booking/<int:booking_id>/', cancel_booking_view, name='cancel_booking'),
]