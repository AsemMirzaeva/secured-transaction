from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-date_joined"]
    list_display = ["phone", "full_name", "phone_verified", "is_operator", "is_staff"]
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Shaxsiy ma'lumot", {"fields": ("full_name",)}),
        ("Ruxsatlar", {"fields": ("is_active", "is_staff", "is_superuser", "is_operator", "groups", "user_permissions")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("phone", "password1", "password2")}),)
    search_fields = ("phone", "full_name")