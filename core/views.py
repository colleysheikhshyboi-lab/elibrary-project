"""
Views for the core/home functionality.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from documents.models import Document, DocumentCategory
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


def home_view(request):
    """
    Home page view.
    """
    # Get recent documents
    recent_documents = Document.objects.filter(
        is_published=True
    ).order_by('-created_at')[:10]
    
    # Get document type statistics
    doc_types = []
    for doc_type in Document.DocumentType.choices:
        count = Document.objects.filter(
            document_type=doc_type[0],
            is_published=True
        ).count()
        if count > 0:
            doc_types.append({
                'name': doc_type[1],
                'slug': doc_type[0],
                'count': count
            })
    
    # Get categories
    categories = DocumentCategory.objects.filter(
        is_active=True
    ).annotate(
        document_count=Count('document')
    ).order_by('-document_count')[:6]
    
    # Get total counts
    stats = {
        'total_documents': Document.objects.filter(is_published=True).count(),
        'total_categories': DocumentCategory.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'core/home.html', {
        'recent_documents': recent_documents,
        'doc_types': doc_types,
        'categories': categories,
        'stats': stats,
        'title': 'National Assembly e-Library'
    })


@login_required
def dashboard_redirect(request):
    """
    Redirect users to appropriate dashboard based on role.
    """
    user = request.user
    
    if user.role in ['admin', 'clerk', 'librarian']:
        return render(request, 'accounts/dashboard_admin.html', {
            'title': 'Dashboard'
        })
    elif user.role == 'mp':
        return render(request, 'accounts/dashboard_mp.html', {
            'title': 'MP Dashboard'
        })
    else:
        return render(request, 'accounts/dashboard_public.html', {
            'title': 'Dashboard'
        })
