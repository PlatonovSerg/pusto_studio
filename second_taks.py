import csv

from django.db import models
from django.utils import timezone


class Player(models.Model):
    player_id = models.CharField(max_length=100)

    def save_level_data_to_file(self, file_path):
        """
        Этот метод лучше хранить вне модели в utils,
        но для наглядности оставил тут.
        """
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["player_id", "level_title", "is_completed", "prize_title"]
            )

            prize_subquery = LevelPrize.objects.filter(
                level=models.OuterRef("level"),
                level__playerlevel__player=models.OuterRef("player"),
            ).values("prize__title")[:1]

            player_levels = (
                PlayerLevel.objects.filter(player=self)
                .annotate(prize_title=models.Subquery(prize_subquery))
                .select_related("level")
                .iterator()
            )

            for player_level in player_levels:
                writer.writerow(
                    [
                        self.player_id,
                        player_level.level.title,
                        player_level.is_completed,
                        (
                            player_level.prize_title
                            if player_level.prize_title
                            else "No Prize"
                        ),
                    ]
                )


class Prize(models.Model):
    title = models.CharField()


class PlayerPrize(models.Model):
    """
    # Добавил модель для связи приза с игроком.
    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ("player", "prize")


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    def assign_prize(self):
        """
        Создает связь между игроком и призом в случае прохождения уровня.
        Через таблицу PlayerPrize
        """
        if self.is_completed:
            level_prize = LevelPrize.objects.filter(level=self.level).first()

            if not level_prize:
                return False

            if not PlayerPrize.objects.filter(
                player=self.player, prize=level_prize.prize
            ).exists():
                PlayerPrize.objects.create(
                    player=self.player,
                    prize=level_prize.prize,
                    received=timezone.now(),
                )
                return True

        return False


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()
