from django.db.models import Avg
from reviews.models import Category, Genre, Title, Review
from api.paginations import (GenreCategoryPagination, TitlePagination)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import filters, status, viewsets, mixins
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from api.permissions import (
    IsAdminOrReadOnly,
    IsAdminUser,
    IsAuthorOrModerPermission,
)
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleCreateSerializer,
    SignupSerializer,
    UserSerializer,
    MeSerializer,
    TokenSerializer,
    CommentSerializer,
    ReviewSerializer)
from user.models import User
from api.code_generator import send_confirmation_code
from api.filters import TitleFilter


class CategoryGenreViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin):

    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = GenreCategoryPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CategoryGenreViewSet):

    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.kwargs.get('version') == 'v1':
            return CategorySerializer


class GenreViewSet(CategoryGenreViewSet):

    queryset = Genre.objects.all()

    def get_serializer_class(self):
        if self.kwargs.get('version') == 'v1':
            return GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):

    queryset = Title.objects.all()
    pagination_class = TitlePagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.kwargs.get('version') == 'v1':
            if self.action in ('create', 'partial_update'):
                return TitleCreateSerializer
            return TitleSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get_serializer_class(self):
        if self.kwargs.get('version') == 'v1':
            return UserSerializer


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        me = get_object_or_404(User, username=request.user.username)
        if self.kwargs.get('version') == 'v1':
            serializer = UserSerializer(me)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        me = get_object_or_404(User, username=request.user.username)
        if self.kwargs.get('version') == 'v1':
            serializer = MeSerializer(me, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(TokenObtainPairView):

    def get_serializer_class(self):
        if self.kwargs.get('version') == 'v1':
            return TokenSerializer


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, **kwargs):
        if self.kwargs.get('version') == 'v1':
            serializer = SignupSerializer(data=request.data)
        if User.objects.filter(username=request.data.get('username'),
                               email=request.data.get('email')).exists():
            send_confirmation_code(request)
            return Response(request.data, status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_confirmation_code(request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):

    """Получение списка всех отзывов без аутентификации,
    получение отзыва по id произведения без аутентификации,
    добавление нового отзыва авторизированным пользователем,
    частичное изменение отзыва авторизировананный пользователем,
    администратором и модератором"""
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrModerPermission)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def get_serializer_class(self):
        if self.kwargs.get('version') == 'v1':
            return ReviewSerializer

    def perform_create(self, serializer, **kwargs):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        if self.kwargs.get('version') == 'v1':
            serializer.save(author=self.request.user, title=title)
        score_avg = Review.objects.filter(title=title).aggregate(Avg('score'))
        title.rating = score_avg['score__avg']
        title.save()


class CommentViewSet(viewsets.ModelViewSet):

    """Реализовано добавление нового комментария к отзыву
    авторизованным пользователем, обновление и удаление комментария
    права у автора, админа и модератора, получить комментарий для
    отзыва по id доступно без авторизации"""
    permission_classes = (
        IsAuthorOrModerPermission,
        IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def get_serializer_class(self):
        if self.kwargs.get('version') == 'v1':
            return CommentSerializer

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
