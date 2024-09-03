# При желании можно развернуть джанго приложение для ручного тестирования.

сам код в README.md, first_task.py/ second_task.py

# FirstTask

```python {"id":"01J6VYGB2C7R02YC9VNPNJSJ6P"}
from django.db import models
from django.utils import timezone


class Player(models.Model):
    """Модель пользователя
    поля:
    username - Имя пользователя или UID/ID, если привязано к другому приложению
    first_login - Дата и время первого входа
    last_login - будет обновляться каждый вход пользователя. Можно получить в middleware или сигналами.
    points - общее количество очков игрока.
    """

    username = models.CharField(max_length=100, unique=True)
    first_login = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now) #необязательное поле.
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} ({self.points} points)"


class Boost(models.Model):
    """
    Boost-ы игрокам. Можно реализовать с помощью choises или подключить
    Поля:
    BOOST_TYPES - Список значений для boost-ов
    type - Какой буст в данный момент у пользователя.
    Методы:
    type_of_boost - определяет, какой вид пуста у пользователя
                    в зависимости от заработанных очков
    """

    BOOST_TYPES = (
        ("foo", "bar"),
        ("foo_one", "bar_one"),
    )

    type = models.CharField(max_length=20, choices=BOOST_TYPES)
    player = models.ForeignKey(
        Player, related_name="boosts", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.type} ,{self.amount} for {self.player.username}"

    @classmethod
    def type_of_boost(cls, player):
        """
        Присваивает буст в зависимости от набранных игроком очков.
        """
        if player.points >= 100 and player.points < 200:
            boost_type = "foo"
        elif player.points >= 200:
            boost_type = "foo_one"
        else:
            return None
        boost = cls(type=boost_type, player=player)
        boost.save()
        return boost


# Пример использования во вьюхах
player = Player.objects.get(username="player_username")
# Получаем игрока из базы данных
boost = Boost.type_of_boost(player)  # Присваиваем буст на основе очков игрока
```

# Second Task

Написать два метода:

1. Присвоение игроку приза за прохождение уровня.
2. Выгрузку в csv следующих данных: id игрока, название уровня, пройден ли уровень, полученный приз за уровень. Учесть, что записей может быть 100 000 и более.

## Task2.1 Присвоение игроку приза за прохождение уровня.

- Добавил метод начисления очков за прохождение уровней.
```python
update_score_and_prizes()
```
так же переопределил метод save для PlayerLevel, чтоб при сохранении в бд игроку добавлялись соответсвующие очки и призы.
- Добавил метод начисления призов за прохождение уровней.
- (к Player добавил поле scores для подсчета общего количества очков, поля avatar, name для стилизации и чтоб ручные тесты было делать приятнее)
- Добавил метод записи в файл(csv) можно возвращать в HttpResponse при необходимости.
```python
save_level_data_to_file()
```

```python {"id":"01J6VYGB2EXN1J3YHVA0VHBC6H"}
import csv

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

```

### Пример выгруженных данных

```csv {"id":"01J6VYGB2EXN1J3YHVA6AD3C5N"}
player_id,level_title,is_completed,prize_title
strong_143345,MediumLevel,True,Beer
strong_143345,EasyLevel,True,Pizza
```