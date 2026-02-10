"""
Context processor to add document statistics to all templates.
"""

from documents.models import Document, DocumentCategory
from django.db.models import Count


def document_stats(request):
    """
    Add document statistics to the template context.
    """
    stats = {
        'total_documents': Document.objects.filter(is_published=True).count(),
        'categories_count': DocumentCategory.objects.filter(is_active=True).count(),
    }
    
    # Add recent documents count
    from django.utils import timezone
    from datetime import timedelta
    
    recent_date = timezone.now() - timedelta(days=7)
    stats['recent_documents'] = Document.objects.filter(
        is_published=True,
        created_at__gte=recent_date
    ).count()
    
    # Add document type counts
    stats['document_types'] = {}
    for doc_type in Document.DocumentType.choices:
        count = Document.objects.filter(
            document_type=doc_type[0],
            is_published=True
        ).count()
        if count > 0:
            stats['document_types'][doc_type[1]] = count
    
    return {
        'document_stats': stats
    }
