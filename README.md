# При желании можно развернуть джанго приложение для ручного тестирования.

код в first_task.py, second_task.py

Как запустить приложение.

```bash
python -m venv venv #создайте виртуальное окружение
source venv/bin/activate #(mac)
source venv/script/activate #(mac)
pip install requirements.txt
cd game #перейдите в директорию с manage.py
alias pm="python manage.py" #для удобства можно прописать алиас для python manage.py
pm migrate
pm createsuperuser #при необходимости можно создать суперпользователя
pm loaddata db_dump.json
pm runserver
```

Или ознакомиться с демонстрацией.

# [demo](https://disk.yandex.ru/i/yz8yaX__UpZ1LQ)

urls:

http://localhost:8000/player/<int:id>/ #просмотр пользователя по ID

http://localhost:8000/load_to_csv/<int:id> #выгрузка данных по пользователю

для добавления данных используйте [admin panel](http://127.0.0.1:8000/admin/)

### Пример выгруженных данных

```csv {"id":"01J6VYGB2EXN1J3YHVA6AD3C5N"}
player_id,level_title,is_completed,prize_title
strong_143345,MediumLevel,True,Beer
strong_143345,EasyLevel,True,Pizza
```