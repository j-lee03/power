# 파일 위치: config/urls.py

from django.contrib import admin
from django.urls import path, include  # 1. include를 꼭 추가해야 합니다!

urlpatterns = [
    path('admin/', admin.site.urls),

    # 2. plans 앱의 urls를 연결하는 코드를 추가합니다.
    # 이렇게 하면 메인 주소로 들어왔을 때 plans 폴더의 urls.py로 안내합니다.
    path('', include('plans.urls')),
]