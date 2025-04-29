from django.contrib import admin
from django.contrib.auth import get_user_model


User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "role", "company")
    list_filter = ("role", "company")
    search_fields = ("username",)
    raw_id_fields = ("company",)
