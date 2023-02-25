import csv
from django.core.management.base import BaseCommand

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

    def handle(self, *args, **options):

        for model, filename in IMPORT_OBJECTS.items():
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
                    model.objects.create(**values)
                self.stdout.write(self.style.SUCCESS('SUCCESS'))
