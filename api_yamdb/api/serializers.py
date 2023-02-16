from reviews.models import Category, Genre, Title
from user.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import get_object_or_404
import datetime as dt


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating', 'description', 'category', 'genre')
        model = Title


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')
        model = Title

    def validate_year(self, value):
        if dt.datetime.now().year < value:
            raise serializers.ValidationError('Некорректная дата выпуска произведения!')
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role',)
        model = User


class MeSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=20)

    def validate(self, data):
        user = get_object_or_404(User, username=data.get('username'))
        if user.confirmation_code != data.get('confirmation_code'):
            raise serializers.ValidationError('Не верный confirmation_code')
        return {'access': str(AccessToken.for_user(user))}


class SignupSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Данное имя недоступно',
            )
        return value

    class Meta:
        fields = ('username', 'email')
        model = User