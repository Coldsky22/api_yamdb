from django.urls import include, re_path, path
from rest_framework import routers

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    MeView,
    UserViewSet,
    create_token,
    create_user)


VERSION_URL = '^(?P<version>(v1))'

router = routers.DefaultRouter()

router.register(
    r'users',
    UserViewSet,
    basename='user',
)
router.register(
    r'categories',
    CategoryViewSet,
    basename='category',
)
router.register(
    r'genres',
    GenreViewSet,
    basename='genre',
)
router.register(
    r'titles',
    TitleViewSet,
    basename='title',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment',
)

urlpatterns = [
    re_path(rf'{VERSION_URL}/auth/', include([
        path('token/', create_token),
        path('signup/', create_user)])),
    re_path(rf'{VERSION_URL}/users/me/',
            MeView.as_view(),
            name='me'
            ),
    re_path(rf'{VERSION_URL}/',
            include(router.urls)
            ),
]
