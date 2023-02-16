from reviews.models import Category, Genre, Title
from user.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import get_object_or_404


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        fields = ('id', 'name', 'year', 'rating', 'description', 'category', 'genre')
        model = Title

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        category = validated_data.pop('category')
        print(category)

        title = Title.objects.create(**validated_data)

        for genre in genres:
            current_genre, created = Genre.objects.get_or_create(**genre)
            title.genre.add(current_genre)
        current_category, status = Category.objects.get_or_create(**category)
        title.category = current_category

        return title


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