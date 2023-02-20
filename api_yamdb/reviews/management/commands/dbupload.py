from django.core.management.base import BaseCommand
import csv
import sqlite3
import datetime
from api import code_generator


class Command(BaseCommand):
    TABLE_NAMES = {
        'category.csv': 'reviews_category',
        'comments.csv': 'reviews_comment',
        'genre.csv': 'reviews_genre',
        'genre_title.csv': 'reviews_title_genre',
        'review.csv': 'reviews_review',
        'titles.csv': 'reviews_title',
        'users.csv': 'user_user',
    }

    USER_DEFAULT_COLUMN = {
        'is_superuser': '0',
        'is_staff': '0',
        'is_active': '1',
        'date_joined': str(datetime.datetime.now()),
    }

    def get_name_columns_from_db(
            self, cursor: sqlite3.Cursor, table_name: str, out_par: int):
        """Возвращает list с названием полей из таблицы БД"""
        name_columns = cursor.execute(
            f"""select * from {table_name} limit 1""")
        if out_par == 0:
            return [str(i[0]) for i in name_columns.description]
        if out_par == 1:
            return ', '.join(str(i[0]) for i in name_columns.description)

    def get_keys_from_dict(self, row: dict):
        """Возвращает строку ключей из словаря"""
        return ', '.join(str(key) for key in row.keys())

    def get_value_from_dict(self, row: dict):
        """Возвращает строку значений из словаря"""
        return ', '.join("'" + str(value) + "'" for value in row.values())

    def clean_table(self, connect: sqlite3.Connection,
                    cursor: sqlite3.Cursor, table_name: str):
        """Очищение таблицы БД."""
        cursor.execute(f"""DELETE FROM {table_name}""")
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
        return (', '.join("'" + str(value).replace("'", "''")
                          + "'" for value in data.values()))

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

    def save_avg_rating(self, connect: sqlite3.Connection,
                        cursor: sqlite3.Cursor):
        """Заполнение среднего рейтинга у произведения."""
        sql_get_titles_id = (
            """
            SELECT id
            FROM reviews_title
            """
        )
        titles_id = cursor.execute(
            sql_get_titles_id).fetchall()

        for title_id in titles_id:
            sql_get_avg_score = (
                f"""
                SELECT AVG(score)
                FROM reviews_review
                WHERE title_id={title_id[0]}
                """
            )
            title_avg_score = cursor.execute(
                sql_get_avg_score).fetchall()

            sql_add_rating = (
                f"""
                UPDATE reviews_title
                SET rating = {int(title_avg_score[0][0])}
                WHERE id = {title_id[0]}
                """
            )
            cursor.execute(sql_add_rating)
        connect.commit()

    def handle(self, *args, **options):
        # Подключение к БД
        con = sqlite3.connect('../api_yamdb/db.sqlite3')
        cur = con.cursor()
        # Перебираем все файлы и соответствцющие таблицы БД
        for file_name, table_name in self.TABLE_NAMES.items():
            # Выводим в терминал информацию о заполнении таблицы
            self.stdout.write(
                f'Заполнение таблицы {table_name}........', ending='')
            # Открываем файл
            with open(
                    'static/data/' + file_name,
                    newline='',
                    encoding='UTF8',
            ) as csvfile:
                reader = csv.DictReader(csvfile, dialect='excel')
                # Очищаем таблицу
                self.clean_table(con, cur, table_name)
                # Построчно считываем данные из файла в виде словаря:
                # "Наименование поля":"Значение поля"
                for row in reader:
                    # Выгружаем названия полей таблицы из БД и
                    # сравниваем с названиями полей в файле.
                    # При необходимости корректируем и возвращаем
                    # итоговый словарь.
                    prep_name_col = self.prep_name_columns(
                        self.get_name_columns_from_db(
                            cur, table_name, 0), row)
                    # Удаляем из словаря поля с незаполненными значениями.
                    data_without_null_value = (self.del_null_values(
                        prep_name_col))
                    # Получаем из словаря строку с названием полей таблицы.
                    name_columns = (self.get_keys_from_dict(
                        data_without_null_value))
                    # Получаем из словаря строку со значениями полей таблицы.
                    values = self.prep_values(data_without_null_value)
                    # Если загружаем данные в таблицу User,
                    # то добавляем значения по умолчанию
                    if file_name == 'users.csv':
                        # Генерируем код подтверждения и
                        # добавляем в словарь дефолтных значений
                        self.USER_DEFAULT_COLUMN['confirmation_code'] = str(
                            code_generator.get_code())
                        # Обогащаем строку с названиями полей таблицы
                        name_columns = (
                            name_columns
                            + ', '
                            + self.get_keys_from_dict(self.USER_DEFAULT_COLUMN)
                        )
                        # Обогащаем строку со значениями полей таблицы
                        values = (
                            values
                            + ', '
                            + self.get_value_from_dict(
                                self.USER_DEFAULT_COLUMN,
                            )
                        )
                    try:
                        # Формируем SQL запрос для вставки строки в таблицу
                        sql_add_row = (
                            f"""
                            INSERT INTO {table_name}
                            ({name_columns})
                            VALUES ({values});
                            """
                        )
                        # Вставляем строку в таблицу БД
                        cur.execute(sql_add_row)
                    except (sqlite3.IntegrityError,
                            sqlite3.OperationalError) as error:
                        # Выводим в терминал статус FAILED заполнения таблицы
                        self.stdout.write(self.style.ERROR('FAILED'))
                        # Вывод информации об ошибке
                        self.stdout.write(
                            f'>>> ОШИБКА. '
                            f'Error: {error}',
                        )
                    con.commit()
                # Выводим в терминал статус SUCCESS заполнения таблицы
                self.stdout.write(self.style.SUCCESS('SUCCESS'))
            csvfile.close()
        # Высчитываем средний рейтинг и сохраняем его в Title.
        self.save_avg_rating(con, cur)
        con.close()
