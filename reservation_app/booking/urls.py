from django.urls import path
from .views import room_list, room_detail, hotel_detail, register_view, login_view, logout_view

urlpatterns = [
    path('', room_list, name='room_list'),
    path('rooms/<int:pk>/', room_detail, name='room_detail'),
    path('hotels/<int:pk>/', hotel_detail, name='hotel_detail'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]