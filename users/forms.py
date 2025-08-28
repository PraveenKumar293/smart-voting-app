# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from datetime import date
from django.core.exceptions import ValidationError

class RegistrationForm(UserCreationForm):
    mobile_number = forms.CharField(max_length=15, required=True)
    aadhaar_number = forms.CharField(max_length=12, required=True)
    voter_id = forms.CharField(max_length=30, required=True)
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = CustomUser
        fields = ('username','email','mobile_number','aadhaar_number','voter_id','dob','password1','password2')

    def clean_dob(self):
        dob = self.cleaned_data['dob']
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise ValidationError("You must be at least 18 years old to register.")
        return dob

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Mobile")
