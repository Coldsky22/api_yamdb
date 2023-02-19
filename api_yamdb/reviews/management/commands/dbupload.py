from django.core.management.base import BaseCommand
import csv
import sqlite3
import datetime


class Command(BaseCommand):
    TABLE_NAMES = {
        'category.csv': 'reviews_category',
        'comments.csv': 'reviews_comment',
        'genre.csv': 'reviews_genre',
        'genre_title.csv': 'reviews_title_genre',
        'review.csv': 'reviews_review',
        'titles.csv': 'reviews_title',
        'users.csv': 'user_user'
    }

    USER_DEFAULT_COLUMN = {
        'is_superuser': '0',
        'is_staff': '0',
        'is_active': '1',
        'date_joined': str(datetime.datetime.now())
    }

    def get_name_columns_from_db(
            self, cursor: sqlite3.Cursor, table_name: str, out_par: int):
        """Возвращает list с названием полей из таблицы БД"""
        name_columns = cursor.execute(
            f'''select * from {table_name} limit 1''')
        if out_par == 0:
            return [str(i[0]) for i in name_columns.description]
        if out_par == 1:
            return ', '.join(str(i[0]) for i in name_columns.description)

    def get_keys_from_dict(self, row: dict):
        """Возвращает строку ключей из словаря"""
        return ', '.join(str(key) for key in row.keys())

    def get_value_from_dict(self, row: dict):
        """Возвращает строку значений из словаря"""
        return ', '.join('\'' + str(value) + '\'' for value in row.values())

    def clean_table(self, connect: sqlite3.Connection,
                    cursor: sqlite3.Cursor, table_name: str):
        """Очищение таблицы БД."""
        cursor.execute(f'''DELETE FROM {table_name}''')
        connect.commit()

    def del_null_values(self, data: dict):
        """Удаление из dict ключей с незаполненными данными.
        Метод возвращает итоговый словать."""
        res_values = {}
        for key, value in data.items():
            if value:
                res_values[key] = value
        return res_values

    def prep_values(self, data: dict):
        """Возвращает форматированную  строку со значениями из словаря.
        Значения в строке перечисляются через (,).
        Экранируется знак (') """
        return (', '.join(
            '\'' + str(value).replace("'", "''") +
            '\'' for value in data.values()
        ))

    def prep_name_columns(self, name_columns_from_db: list,
                          row: dict):
        """Возвращает словарь с корректными заголовками полей таблицы."""
        res_dict = {}
        for key, value in row.items():
            new_key = str(key) + '_id'
            if new_key in name_columns_from_db:
                res_dict[new_key] = value
            else:
                res_dict[key] = value
        return res_dict

    def handle(self, *args, **options):
        con = sqlite3.connect('../api_yamdb/db.sqlite3')
        cur = con.cursor()
        for file_name, table_name in self.TABLE_NAMES.items():
            self.stdout.write(f'Заполнение таблицы {table_name}........', ending='')
            with open(
                    'static/data/' + file_name,
                    newline='',
                    encoding='UTF8'
            ) as csvfile:
                reader = csv.DictReader(csvfile, dialect='excel')
                self.clean_table(con, cur, table_name)
                for row in reader:
                    prep_name_col = self.prep_name_columns(
                        self.get_name_columns_from_db(
                            cur, table_name, 0), row)

                    data_without_null_value = (self.del_null_values(
                        prep_name_col))

                    name_columns = (self.get_keys_from_dict(
                        data_without_null_value))

                    values = self.prep_values(data_without_null_value)

                    if file_name == 'users.csv':
                        name_columns = (
                                name_columns + ', ' +
                                self.get_keys_from_dict(
                                    self.USER_DEFAULT_COLUMN))

                        values = (values + ', ' +
                                  self.get_value_from_dict(
                                      self.USER_DEFAULT_COLUMN))
                    try:
                        cur.execute(f'''INSERT INTO {table_name}
                        ({name_columns})VALUES ({values});''')
                    except sqlite3.IntegrityError:
                        self.stdout.write(self.style.ERROR('FAILED'))
                        self.stdout.write(
                            f">>> ОШИБКА. "
                            f"Проверка на уникальность в "
                            f"таблице {table_name}.\n "
                            f"Обнаружен дубликат записи в "
                            f"файле {file_name}.\n"
                            f"{values}"
                        )
                    except sqlite3.OperationalError:
                        self.stdout.write(self.style.ERROR('FAILED'))
                        self.stdout.write(
                            "ОШИБКА. Некорректно заполнены данные")
                    con.commit()
                self.stdout.write(self.style.SUCCESS('SUCCESS'))
            csvfile.close()
        con.close()
