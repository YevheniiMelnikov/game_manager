from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Company, Game, GameSession, GameResults

User = get_user_model()


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "role", "company")
    list_filter = ("role", "company")
    search_fields = ("username",)
    raw_id_fields = ("company",)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "language", "category")
    search_fields = ("name", "language", "category")


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "game", "start_datetime")
    list_filter = ("game", "start_datetime")
    search_fields = ("game__name",)
    filter_horizontal = ("participants",)


@admin.register(GameResults)
class GameResultsAdmin(admin.ModelAdmin):
    list_display = ("id", "game_session", "score", "is_completed")
    list_filter = ("is_completed",)
    search_fields = ("game_session__game__name",)
