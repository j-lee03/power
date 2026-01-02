from django.shortcuts import render
from django.http import HttpResponse, Http404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

def document_list(request):
    documents = Document.objects.all().order_by('-created_at')
    return render(request, 'plans/document_list.html', {'documents': documents})

def serve_pdf_from_db(request, doc_id):
    try:
        doc = Document.objects.get(id=doc_id)
        if not doc.file_data:
            raise Http404()

        response = HttpResponse(doc.file_data, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{doc.filename}"'
        return response
    except Document.DoesNotExist:
        raise Http404()