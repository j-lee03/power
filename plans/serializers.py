from rest_framework import serializers
from .models import EventDocument

class DocumentSerializer(serializers.ModelSerializer):
    # API 결과에 직급 이름(예: "파트장")을 보여주기 위한 읽기 전용 필드
    read_level_display = serializers.CharField(source='get_read_level_display', read_only=True)
    write_level_display = serializers.CharField(source='get_write_level_display', read_only=True)

    class Meta:
        model = EventDocument
        fields = [
            'id', 'title', 'content', 'pdf_file',
            'read_level', 'read_level_display',   # 공개 범위 설정
            'write_level', 'write_level_display', # 수정 권한 설정
            'uploaded_at'
        ]
        read_only_fields = ['uploaded_at']