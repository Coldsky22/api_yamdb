import csv
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    TitleGenre,
)
from user.models import User


IMPORT_OBJECTS = {
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    TitleGenre: 'genre_title.csv',
    User: 'users.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):

    help = 'Заполнение БД тестовыми данными из CSV файлов.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Удаление записей из таблицы перед добавлением данных.',
        )

    def handle(self, *args, **options):

        for model, filename in IMPORT_OBJECTS.items():
            if options['delete']:
                model_obj = model.objects.all()
                model_obj.delete()
            self.stdout.write(
                f'Загрузка файла {filename}........', ending='')
            with open(
                    'static/data/' + filename,
                    newline='',
                    encoding='UTF8',
            ) as csvfile:
                reader = csv.DictReader(csvfile, dialect='excel')
                create_list = []
                for values in reader:
                    if filename == 'titles.csv':
                        category = Category.objects.get(
                            id=values.get('category'))
                        values['category'] = category
                    elif (
                        (filename == 'review.csv') or (
                            filename == 'comments.csv')):
                        author = User.objects.get(id=values.get('author'))
                        values['author'] = author
                    create_list.append(model(**values))
                try:
                    model.objects.bulk_create(create_list)
                except IntegrityError:
                    self.stdout.write(self.style.ERROR('FAILED'))
                    self.stdout.write('Нарушена уникальность данных.')
                else:
                    self.stdout.write(self.style.SUCCESS('SUCCESS'))
