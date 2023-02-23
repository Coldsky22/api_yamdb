# Generated by Django 3.2 on 2023-02-23 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20230223_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(max_length=256, verbose_name='наименование жанра'),
        ),
        migrations.AlterField(
            model_name='title',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reviews.category', verbose_name='категория'),
        ),
        migrations.AlterField(
            model_name='title',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='title',
            name='genre',
            field=models.ManyToManyField(blank=True, null=True, to='reviews.Genre', verbose_name='жанр'),
        ),
        migrations.AlterField(
            model_name='title',
            name='name',
            field=models.TextField(max_length=256, verbose_name='наименование'),
        ),
        migrations.AlterField(
            model_name='title',
            name='rating',
            field=models.IntegerField(null=True, verbose_name='рейтинг'),
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.IntegerField(verbose_name='год'),
        ),
    ]
