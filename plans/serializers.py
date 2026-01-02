from rest_framework import serializers
from .models import EventDocument

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
    class Meta:
        model = EventDocument
        fields = [
            'id', 'title', 'content', 'pdf_file',
            'read_level', 'read_level_display',   # 공개 범위
            'write_level', 'write_level_display', # 수정 권한
            'uploaded_at'
        ]
        read_only_fields = ['uploaded_at']