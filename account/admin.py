from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("phone", "is_staff", "is_active",)
    list_filter = ("phone", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Permissions", {"fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone", "password1", "password2", "is_staff",
                "is_superuser", "is_active", "groups", "user_permissions"
            )}
         ),
    )
    search_fields = ("phone",)
    ordering = ("phone",)
