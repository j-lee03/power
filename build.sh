#!/usr/bin/env bash
# 에러 발생 시 즉시 중단
set -o errexit

# 1. 라이브러리 설치
pip install -r requirements.txt

# 2. 정적 파일 수집
python manage.py collectstatic --no-input

# 3. 데이터베이스 적용 (PostgreSQL 연결 시 자동 실행됨)
python manage.py migrate
python create_admin.py