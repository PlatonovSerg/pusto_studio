from django.shortcuts import get_object_or_404, render

from .models import Level, LevelPrize, Player, PlayerLevel, Prize


def main(request, id):
    title = "Player with ID: {id}"
    template = "player.html"
    player = get_object_or_404(Player, id=id)
    player_prizes = LevelPrize.objects.filter(
        level__playerlevel__player=player,
        level__playerlevel__is_completed=True,
        received__isnull=False,
    )
    completed_levels_count = PlayerLevel.objects.filter(
        player=player, is_completed=True
    ).count()
    context = {
        "player": player,
        "title": title,
        "player_prizes": player_prizes,
        "completed_levels_count": completed_levels_count,
    }

    return render(request, template, context=context)
