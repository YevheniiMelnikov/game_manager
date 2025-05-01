from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "role", "company", "created", "is_active")
    list_filter = ("role", "company", "is_active", "created")
    search_fields = ("username", "company__name")
    raw_id_fields = ("company",)
    readonly_fields = ("created", "updated")
