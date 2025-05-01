from django.contrib import admin
from .models import Company, Game, GameSession, GameResults


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "language", "category")
    search_fields = ("name", "language", "category")
    readonly_fields = ("created_at", "updated_at")


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "game", "start_datetime")
    list_filter = ("game", "start_datetime")
    search_fields = ("game__name",)
    autocomplete_fields = ("participants",)
    list_select_related = ("game",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(GameResults)
class GameResultsAdmin(admin.ModelAdmin):
    list_display = ("id", "game_session", "score", "is_completed")
    list_filter = ("is_completed",)
    search_fields = ("game_session__game__name",)
    list_select_related = ("game_session",)
    readonly_fields = ("created_at", "updated_at")
