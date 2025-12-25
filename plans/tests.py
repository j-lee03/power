from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import EventDocument, Profile

class DocumentSystemTest(APITestCase):

    # [1] 테스트 전 준비작업 (가상의 사용자 만들기)
    def setUp(self):
        # 1. 하객 (Guest) - 권한 0
        self.guest_user = User.objects.create_user(username='guest', password='password')
        # Profile은 Signal에 의해 자동 생성되므로 수정만 함
        self.guest_user.profile.role = 0
        self.guest_user.profile.save()

        # 2. 스태프 (Staff) - 권한 1
        self.staff_user = User.objects.create_user(username='staff', password='password')
        self.staff_user.profile.role = 1
        self.staff_user.profile.save()

        # 3. 팀장 (Manager) - 권한 2
        self.manager_user = User.objects.create_user(username='manager', password='password')
        self.manager_user.profile.role = 2
        self.manager_user.profile.save()

        # API 접속 주소 (/api/docs/)
        self.url = '/api/docs/'

    # [시나리오 1] 하객(Guest)은 문서를 업로드하면 실패해야 한다 (403 Forbidden)
    def test_guest_cannot_upload(self):
        self.client.force_authenticate(user=self.guest_user) # 하객으로 로그인
        data = {'title': '하객이 쓴 문서'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # [시나리오 2] 스태프(Staff)는 문서를 업로드하면 성공해야 한다 (201 Created)
    def test_staff_can_upload_pdf(self):
        self.client.force_authenticate(user=self.staff_user) # 스태프로 로그인

        # 가짜 PDF 파일 생성
        pdf = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        data = {
            'title': '음향 큐시트',
            'pdf_file': pdf,
            'read_level': 1, # 스태프 이상 열람
            'write_level': 2 # 팀장 이상 수정
        }

        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 실제로 DB에 저장됐는지 확인
        self.assertEqual(EventDocument.objects.count(), 1)
        self.assertEqual(EventDocument.objects.get().title, '음향 큐시트')

    # [시나리오 3] 스태프 등급 문서는 하객에게 보이면 안 된다
    def test_read_permission_logic(self):
        # (상황) DB에 '스태프용 문서'가 1개 있음
        doc = EventDocument.objects.create(title="스태프 전용", read_level=1)

        # 1. 하객이 조회 -> 목록이 비어있어야 함 ([])
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 0) # 0개여야 함

        # 2. 스태프가 조회 -> 목록에 1개 있어야 함
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1) # 1개여야 함
        self.assertEqual(response.data[0]['title'], "스태프 전용")

    # [시나리오 4] 삭제 권한 테스트 (팀장만 삭제 가능)
    def test_delete_permission(self):
        # (상황) 삭제 레벨이 2(Manager)인 문서 생성
        doc = EventDocument.objects.create(title="삭제 테스트", write_level=2)
        url_detail = f"{self.url}{doc.id}/"

        # 1. 스태프가 삭제 시도 -> 실패 (403)
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. 팀장이 삭제 시도 -> 성공 (204)
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EventDocument.objects.count(), 0) # DB에서 사라짐