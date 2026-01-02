from rest_framework import viewsets, permissions, exceptions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import EventDocument
from .models import Document
from .serializers import DocumentSerializer
class DocumentViewSet(viewsets.ModelViewSet):

    queryset = EventDocument.objects.all()

    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def document_list(request):
        documents = Document.objects.all().order_by('-created_at')
        return render(request, 'plans/document_list.html', {'documents': documents})

    def get_queryset(self):

        user_role = getattr(self.request.user, 'profile', None) and self.request.user.profile.role or 0


        return EventDocument.objects.filter(read_level__lte=user_role)


    def perform_create(self, serializer):
        user_role = getattr(self.request.user, 'profile', None) and self.request.user.profile.role or 0


        if user_role < 0:
            raise exceptions.PermissionDenied("업로드 권한이 없습니다.")

        serializer.save()


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
