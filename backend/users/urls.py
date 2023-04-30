from rest_framework.routers import DefaultRouter
from django.urls import include, path
from django.conf.urls import url

from api.views import CustomUserViewSet


router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]