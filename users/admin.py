from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTP

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username','email','mobile_number','aadhaar_number','is_area_admin','is_staff')
    fieldsets = UserAdmin.fieldsets + (('Extra Fields', {'fields': ('mobile_number','aadhaar_number','voter_id','dob','has_voted','is_area_admin')}),)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTP)
