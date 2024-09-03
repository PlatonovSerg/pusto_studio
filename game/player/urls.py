from django.urls import path

from .views import load_to_csv, main

app_name = "play"


urlpatterns = [
    path("player/<int:id>/", main, name="player"),
    path("load_to_csv/<int:id>/", load_to_csv, name="load_to_csv"),
]
