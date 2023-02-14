from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (CategoryViewSet,
                    GenreViewSet)


router = SimpleRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)


urlpatterns = [
    path('', include(router.urls))
]
