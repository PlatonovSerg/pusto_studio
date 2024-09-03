from django.db import models
from django.utils import timezone


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title}"


class Prize(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title}"


class PlayerLevel(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_completed:
            self.player.update_score_and_prizes()


class Player(models.Model):
    name = models.CharField(max_length=25)
    player_id = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to="posts/%Y/%m/%d/", blank=True)
    total_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player_id}"

    def update_score_and_prizes(self):
        completed_levels = PlayerLevel.objects.filter(
            player=self, is_completed=True
        )

        self.total_score = 0

        for player_level in completed_levels:
            self.total_score += player_level.score

            level_prizes = LevelPrize.objects.filter(level=player_level.level)
            for level_prize in level_prizes:
                if level_prize.received is None:
                    level_prize.received = timezone.now()
                    level_prize.save()

        self.save()


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.level} - {self.prize}, {self.received}"