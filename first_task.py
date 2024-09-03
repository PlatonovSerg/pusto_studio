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
