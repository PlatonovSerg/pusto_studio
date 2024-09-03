# FirstTask

```python
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
    last_login = models.DateTimeField(default=timezone.now)
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
        return f"{self.type} x{self.amount} for {self.player.username}"

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

Задача:

Дано несколько моделей
```python
from django.db import models

class Player(models.Model):
    player_id = models.CharField(max_length=100)
    
    
class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    
    
    
class Prize(models.Model):
    title = models.CharField()
    
    
class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    
    
class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()
```
Написать два метода:

1. Присвоение игроку приза за прохождение уровня.
2. Выгрузку в csv следующих данных: id игрока, название уровня, пройден ли уровень, полученный приз за уровень. Учесть, что записей может быть 100 000 и более.
     

### Присвоение приза игроку в зависимости от уровня
```python
from datetime import datetime
from django.db import transaction

class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    def assign_prize(self):
        if self.is_completed:
            prize = Prize.objects.filter(levelprize__level=self.level).first()
            if prize:
                with transaction.atomic():
                    LevelPrize.objects.create(
                        level=self.level,
                        prize=prize,
                        received=datetime.now()
                    )
                return True
        return False
```
### Выгрузка в csv 
#### Лучше вынести в utils, но для наглядности присвоил классу.
```python
#можно возвращать в httpResponse, но для наглядности выгрузка в файл.
def save_level_data_to_file(self, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['player_id', 'level_title', 'is_completed', 'prize_title'])

        prize_subquery = LevelPrize.objects.filter(
            level=OuterRef('level'),
            level__playerlevel__player=OuterRef('player')
        ).values('prize__title')[:1]

        player_levels = PlayerLevel.objects.filter(player=self).annotate(
            prize_title=Subquery(prize_subquery)
        ).select_related('level').iterator()

        for player_level in player_levels:
            writer.writerow([
                self.player_id,
                player_level.level.title,
                player_level.is_completed,
                player_level.prize_title if player_level.prize_title else 'No Prize'
                  ])
```