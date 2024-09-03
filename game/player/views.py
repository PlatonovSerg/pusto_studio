from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, get_list_or_404

from .models import LevelPrize, Player, PlayerLevel, Level


def load_to_csv(request, id):
    player = get_object_or_404(Player, id=id)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="player_{id}_data.csv"'
    )

    # Вызываем метод модели для создания CSV-файла
    player.save_level_data_to_file("/tmp/player_data.csv")

    # Открываем созданный файл и отправляем его в ответе
    with open("/tmp/player_data.csv", "r") as csvfile:
        response.write(csvfile.read())

    return response


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


def level_page(request, id):
    player = get_object_or_404(Player, id=id)
    level_complete_players = PlayerLevel.objects.filter(
        player=player, is_completed=True
    )
    title = "Levels"
    levels = get_list_or_404(Level)
    template = "levels.html"
    context = {
        "levels": levels,
        "title": title,
        "level_complete_players": level_complete_players,
    }
    return render(request, template, context=context)
