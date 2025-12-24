from rest_framework import serializers
from .models import EventDocument

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDocument
        fields = ['id', 'title', 'content', 'pdf_file', 'read_level', 'write_level', 'uploaded_at']
        read_only_fields = ['uploaded_at']