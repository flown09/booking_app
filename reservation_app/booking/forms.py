from .models import Booking
from django.forms import DateInput
from django.contrib.auth.forms import UserCreationForm


from django import forms
from .models import CustomUser

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'email', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border rounded p-2'
            })


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
        model = CustomUser
        fields = ['email', 'last_name', 'first_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'w-full border rounded p-2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'].widget.attrs.update({'class': 'w-full border rounded p-2'})
        self.fields['first_name'].widget.attrs.update({'class': 'w-full border rounded p-2'})
        self.fields['password1'].widget.attrs.update({'class': 'w-full border rounded p-2'})
        self.fields['password2'].widget.attrs.update({'class': 'w-full border rounded p-2'})

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'w-full border rounded p-2'})
        self.fields['password'].widget.attrs.update({'class': 'w-full border rounded p-2'})
