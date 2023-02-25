from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from user.models import User


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='наименование категории',
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='наименование жанра',
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)


class Title(models.Model):
    name = models.TextField(
        max_length=256,
        verbose_name='наименование',
    )
    year = models.IntegerField(
        verbose_name='год',
    )
    rating = models.IntegerField(
        null=True,
        verbose_name='рейтинг',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='описание',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='категория',
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        null=True,
        through='TitleGenre',
        verbose_name='жанр',
    )

    class Meta:
        ordering = ('-id',)


class TitleGenre(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
    )


class Review(models.Model):
    """модель написания отзывов, на одно производение,
    одним пользователем, может быть написан только один отзыв"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField(
        max_length=200,
        verbose_name='текст отзыва',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор отзыва',
    )
    score = models.IntegerField(
        verbose_name='оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10),
        ),
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique review',
            )]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """модель создания комментариев к отзывам на произведение"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='текст комментария',
        max_length=200,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор комментария',
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text
