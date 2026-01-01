from rest_framework import viewsets, permissions, exceptions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import EventDocument
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    # [★ 추가된 부분] 이 줄이 있어야 에러가 나지 않습니다.
    queryset = EventDocument.objects.all()

    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    # [1] 열람 제한 로직 (Filtering)
    def get_queryset(self):
        # 1. 내 직급(Role) 확인
        user_role = getattr(self.request.user, 'profile', None) and self.request.user.profile.role or 0

        # 2. 문서의 '공개 범위'보다 내 직급이 높거나 같은 문서만 가져옴
        return EventDocument.objects.filter(read_level__lte=user_role)

    # [2] 문서 업로드 로직
    def perform_create(self, serializer):
        user_role = getattr(self.request.user, 'profile', None) and self.request.user.profile.role or 0

        # (선택사항) 최소 '스텝(0)' 이상만 업로드 가능
        if user_role < 0:
            raise exceptions.PermissionDenied("업로드 권한이 없습니다.")

        serializer.save()

    # [3] 수정/삭제 권한 체크
    def check_write_permission(self, instance):
        user_role = getattr(self.request.user, 'profile', None) and self.request.user.profile.role or 0
        if user_role < instance.write_level:
            raise exceptions.PermissionDenied("이 문서를 수정/삭제할 등급이 부족합니다.")

    def perform_update(self, serializer):
        self.check_write_permission(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self.check_write_permission(instance)
        instance.delete()
