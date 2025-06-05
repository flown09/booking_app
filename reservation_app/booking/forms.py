from django import forms
from .models import Booking
from django.forms import DateInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import CustomUser

class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out']
        widgets = {
            'check_in': DateInput(attrs={'type': 'date'}),
            'check_out': DateInput(attrs={'type': 'date'}),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
