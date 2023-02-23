from django.db.models import Avg
from reviews.models import Category, Genre, Title, Review
from api.paginations import (GenreCategoryPagination, TitlePagination)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from smtplib import SMTPResponseException
from django.conf import settings
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import filters, status, viewsets, mixins
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.decorators import action, api_view, permission_classes

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
    UserSerializer,
    MeSerializer,
    TokenSerializer,
    CommentSerializer,
    ReviewSerializer,
    CreateUserSerializer)
from user.models import User
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

    @action(
        detail=False,
        methods=(['GET', 'PATCH']),
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """Получение данных своей учётной записи."""
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        serializer = UserSerializer(
            request.user, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request, version):
    """Создание нового пользователя."""
    if version == 'v1':
        serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    user, _ = User.objects.get_or_create(username=username, email=email)
    token = default_token_generator.make_token(user)
    user.confirmation_code = token
    user.save()

    try:
        send_mail(
            'confirmation code',
            token,
            settings.MAILING_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    except SMTPResponseException:
        user.delete()
        return Response(
            data={'error': 'Ошибка при отправки кода подтверждения!'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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


@api_view(["POST"])
@permission_classes([AllowAny])
def create_token(request, version):
    if version == 'v1':
        serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=request.data.get('username'),
    )
    if default_token_generator.check_token(
            user,
            request.data.get('confirmation_code'),
    ):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
