from django.urls import path, include
from rest_framework import routers
from .views import (CategoryViewSet, GenreViewSet,
                    TitleViewSet,
                    SignupView,
                    MeView,
                    UserViewSet,
                    TokenView,)
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

urlpatterns = [
    path('auth/token/', TokenView.as_view(),
         name='create_token'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('users/me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]