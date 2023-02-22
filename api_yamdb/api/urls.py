from django.urls import include, re_path
from rest_framework import routers

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupView,
    TitleViewSet,
    MeView,
    UserViewSet,
    TokenView,
)

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
    re_path(r'^(?P<version>(v1))/auth/token/',
            TokenView.as_view(),
            name='create_token'
            ),
    re_path(r'^(?P<version>(v1))/auth/signup/',
            SignupView.as_view(),
            name='signup'
            ),
    re_path(r'^(?P<version>(v1))/users/me/',
            MeView.as_view(),
            name='me'
            ),
    re_path(r'^(?P<version>(v1))/',
            include(router.urls)
            ),
]
