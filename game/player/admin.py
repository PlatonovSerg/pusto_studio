from django.contrib import admin

from .models import Level, LevelPrize, Player, PlayerLevel, Prize


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    fields = ("player_id", 'name', 'avatar', "total_score")


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    fields = (
        "title",
        "order",
    )


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    fields = ("title",)


@admin.register(LevelPrize)
class LevelPrizeAdmin(admin.ModelAdmin):
    fields = (
        "level",
        "prize",
        "received",
    )


@admin.register(PlayerLevel)
class PlayerLevelAdmin(admin.ModelAdmin):
    fields = (
        "player",
        "level",
        "completed",
        "is_completed",
        "score",
    )
