


from django.contrib import admin
from django.urls import path, include  # 1. include를 꼭 추가해야 합니다!

urlpatterns = [
    path('admin/', admin.site.urls),


    path('', include('plans.urls')),
]