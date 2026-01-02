
import os
import django
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():

    username = os.environ.get('SUPER_ID')
    password = os.environ.get('SUPER_PW')

    if not username or not password:
        print("⚠️ 환경 변수(SUPER_ID, SUPER_PW)가 없어서 관리자 생성을 건너뜁니다.")
        return


    if User.objects.filter(username=username).exists():
        print(f"✅ 관리자 계정 '{username}'이(가) 이미 존재합니다.")
    else:

        User.objects.create_superuser(username=username, email='', password=password)
        print(f"🎉 관리자 계정 '{username}' 생성 완료!")

if __name__ == '__main__':
    create_superuser()