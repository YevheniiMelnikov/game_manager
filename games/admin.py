from django.contrib import admin
from .models import Company, Participant, Game, GameSession, GameResults


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "company")
    list_filter = ("role", "company")
    search_fields = ("user__username",)
    raw_id_fields = ("user",)


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
    list_display = ("id", "game_session", "score", "status", "is_completed")
    list_filter = ("status", "is_completed")
    search_fields = ("game_session__game__name",)
