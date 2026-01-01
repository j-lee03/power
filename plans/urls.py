# 파일 위치: plans/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet

router = DefaultRouter()
router.register(r'docs', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]