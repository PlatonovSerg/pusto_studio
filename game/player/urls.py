from django.urls import include, path
from .views import main

app_name = "play"


urlpatterns = [path("player/<int:id>/", main, name="player")]
