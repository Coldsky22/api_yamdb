# api_yamdb
### Описание проекта
Проект YaMDb реализует backend по сбору отзывов пользователей на различные произведения. 
Интерфейс взаимодействия с frontend-ом реализован на основе api.

Подробная документация будет доступна по адресу ```you-domen/redoc/```
после разворачивания проекта.

### Как запустить проект:

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

**(Опционально)** Заполнить БД тестовыми 
данными на основе загрузки из CSV файлов:

```
python manage.py dbupload
```

Запустить проект:

```
python3 manage.py runserver
```

### Над проектом работали:
* Команда Яндекс.Практикум - _costumer_
* Денис Калинин - _team lead_
* Екатерина Данова - _developer_
* Станислав Киркин - _developer_