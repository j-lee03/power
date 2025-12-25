from rest_framework import viewsets, permissions, exceptions  # [수정] exceptions 추가
from rest_framework.parsers import MultiPartParser, FormParser
from .models import EventDocument
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = EventDocument.objects.all()
    serializer_class = DocumentSerializer

    # [핵심] 파일 업로드 처리를 위한 설정
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    # 1. 목록 조회 (권한 필터링)
    def get_queryset(self):
        # 프로필이 없는 경우(에러방지) 0으로 처리
        user_role = getattr(self.request.user, 'profile', None) and self.request.user.profile.role or 0
        return EventDocument.objects.filter(read_level__lte=user_role)

    # 2. 문서 생성 (업로드)
    def perform_create(self, serializer):
        user_role = self.request.user.profile.role
        if user_role < 1: # 최소 STAFF 이상
            # [수정] permissions.PermissionDenied -> exceptions.PermissionDenied
            raise exceptions.PermissionDenied("업로드 권한이 없습니다.")
        serializer.save()

    # 3. 문서 수정/삭제 권한 체크 함수
    def check_write_permission(self, instance):
        user_role = self.request.user.profile.role
        if user_role < instance.write_level:
            # [수정] permissions.PermissionDenied -> exceptions.PermissionDenied
            raise exceptions.PermissionDenied("수정/삭제 권한이 부족합니다.")

    def perform_update(self, serializer):
        self.check_write_permission(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self.check_write_permission(instance)
        instance.delete()
