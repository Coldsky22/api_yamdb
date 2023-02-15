from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework import routers
from .views import (CategoryViewSet, GenreViewSet,
                    TitleViewSet,
                    SignupView,
                    SignupView,
                    MeView,
                    UserViewSet,
                    TokenView,)

router = SimpleRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)


urlpatterns = [
    path('', include(router.urls))
]
router = routers.DefaultRouter()
router.register(
    r'users',
    UserViewSet,
    basename='user',
)

urlpatterns = [
    path('auth/token/', TokenView.as_view(),
         name='create_token'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('users/me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]

# urlpatterns = [
#     path('v1/users/me/', MeView.as_view(), name='users'),
#     path('v1/users/<slug:username>/', UserViewSet.as_view()),
#     path('v1/users/me/', MeView.as_view(), name='me'),
#     path('v1/auth/signup/', SignupView.as_view(), name='sign_up'),
#     path('v1/auth/token/', TokenView.as_view(), name='activation'),
#     path('v1/', include(router.urls)),
# ]

