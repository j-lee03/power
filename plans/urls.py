from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, document_list, serve_pdf_from_db

router = DefaultRouter()
router.register(r'api/docs', DocumentViewSet)

urlpatterns = [
    path('', document_list, name='document-list'),
    path('', include(router.urls)),
]