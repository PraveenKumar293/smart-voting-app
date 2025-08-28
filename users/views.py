# users/views.py
import os, random
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.utils import timezone
from django.conf import settings
from .forms import RegistrationForm, LoginForm
from .models import CustomUser, OTP
from twilio.rest import Client

def _send_sms(to, body):
    """Send SMS via Twilio if configured; otherwise print to console (dev)."""
    sid = getattr(settings, 'TWILIO_SID', None)
    token = getattr(settings, 'TWILIO_TOKEN', None)
    from_num = getattr(settings, 'TWILIO_FROM', None)
    if sid and token and from_num:
        Client(sid, token).messages.create(body=body, from_=from_num, to=to)
    else:
        print(f"[MOCK SMS] to {to}: {body}")

def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True   # set False if you want admin approval before login
            user.save()
            messages.success(request, "Registered successfully. Please verify OTP sent to your mobile.")
            # auto send OTP after registration
            code = f"{random.randint(100000,999999)}"
            expires = timezone.now() + timedelta(minutes=5)
            OTP.objects.create(user=user, code=code, purpose='login', expires_at=expires)
            _send_sms(user.mobile_number, f"Your registration OTP is {code}")
            return redirect('users:verify_otp', user_id=user.id, purpose='login')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def send_otp_view(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')
        try:
            user = CustomUser.objects.get(mobile_number=mobile)
        except CustomUser.DoesNotExist:
            messages.error(request, "Mobile not registered.")
            return redirect('users:login')
        code = f"{random.randint(100000,999999)}"
        expires = timezone.now() + timedelta(minutes=5)
        OTP.objects.create(user=user, code=code, purpose='login', expires_at=expires)
        _send_sms(user.mobile_number, f"Your OTP is {code}")
        messages.success(request, f"OTP sent to {user.mobile_number}")
        return redirect('users:verify_otp', user_id=user.id, purpose='login')
    return render(request, 'users/send_otp.html')

def verify_otp_view(request, user_id, purpose='login'):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        code = request.POST.get('code')
        otp = OTP.objects.filter(user=user, purpose=purpose, used=False).order_by('-created_at').first()
        if otp and otp.is_valid() and otp.code == code:
            otp.used = True
            otp.save()
            user.is_active = True
            user.save()
            # if purpose is login, log the user in
            if purpose == 'login':
                auth.login(request, user)
            messages.success(request, "OTP verified.")
            return redirect('home')
        else:
            messages.error(request, "Invalid or expired OTP.")
    return render(request, 'users/verify_otp.html', {'user': user, 'purpose': purpose})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    auth.logout(request)
    return redirect('users:login')
