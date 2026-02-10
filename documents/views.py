"""
Views for document management.
Handles document upload, viewing, downloading, and search.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods
from django.template.defaultfilters import filesizeformat
from .models import Document, DocumentCategory, DocumentVersion, DocumentAccessLog
from .forms import DocumentForm, DocumentSearchForm
import os


@login_required
def document_list(request):
    """
    Display list of documents with filtering and search.
    """
    documents = Document.objects.filter(is_published=True)
    
    # Apply filters
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    category = request.GET.get('category')
    if category:
        documents = documents.filter(category__slug=category)
    
    year = request.GET.get('year')
    if year:
        documents = documents.filter(year=year)
    
    access_level = request.GET.get('access')
    if access_level:
        documents = documents.filter(access_level=access_level)
    
    # Search
    search_form = DocumentSearchForm(request.GET)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        query = search_form.cleaned_data['q']
        documents = documents.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(keywords__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(documents, 20)
    page = request.GET.get('page')
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)
    
    # Get categories for filter sidebar
    categories = DocumentCategory.objects.filter(is_active=True)
    
    # Get document types with counts
    doc_types = []
    for doc_type_choice in Document.DocumentType.choices:
        count = Document.objects.filter(
            document_type=doc_type_choice[0],
            is_published=True
        ).count()
        doc_types.append((doc_type_choice[0], doc_type_choice[1], count))
    
    return render(request, 'documents/document_list.html', {
        'documents': documents,
        'categories': categories,
        'doc_types': doc_types,
        'search_form': search_form,
        'title': 'Document Library'
    })


@login_required
def document_detail(request, slug):
    """
    Display document details and track access.
    """
    document = get_object_or_404(Document, slug=slug)
    
    # Check access permissions
    if document.access_level != Document.AccessLevel.PUBLIC:
        if not request.user.can_access_restricted:
            return HttpResponseForbidden("You don't have permission to access this document.")
    
    # Track view
    document.increment_view()
    DocumentAccessLog.objects.create(
        document=document,
        user=request.user,
        action=DocumentAccessLog.Action.VIEW,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Get versions if any
    versions = document.versions.all()[:5]
    
    # Get related documents
    related_docs = Document.objects.filter(
        document_type=document.document_type,
        is_published=True
    ).exclude(id=document.id)[:5]
    
    # Get keywords as a list (for template iteration)
    keywords_list = [k.strip() for k in document.keywords.split(',')] if document.keywords else []
    
    return render(request, 'documents/document_detail.html', {
        'document': document,
        'versions': versions,
        'related_docs': related_docs,
        'keywords_list': keywords_list,
        'title': document.title
    })


@login_required
@permission_required('documents.add_document')
def document_upload(request):
    """
    Upload a new document.
    """
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                document = form.save(commit=False)
                document.uploaded_by = request.user
                document.save()
                
                # Create initial version
                DocumentVersion.objects.create(
                    document=document,
                    version='1.0',
                    file=document.file,
                    changes='Initial upload',
                    uploaded_by=request.user
                )
                
                # Create access log
                DocumentAccessLog.objects.create(
                    document=document,
                    user=request.user,
                    action=DocumentAccessLog.Action.EDIT,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details='Document uploaded'
                )
                
                messages.success(request, 'Document uploaded successfully.')
                return redirect('documents:document_detail', slug=document.slug)
    else:
        form = DocumentForm()
    
    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': 'Upload Document'
    })


@login_required
@permission_required('documents.change_document')
def document_edit(request, slug):
    """
    Edit an existing document.
    """
    document = get_object_or_404(Document, slug=slug)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            with transaction.atomic():
                document = form.save()
                
                # Track edit
                DocumentAccessLog.objects.create(
                    document=document,
                    user=request.user,
                    action=DocumentAccessLog.Action.EDIT,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details='Document updated'
                )
                
                messages.success(request, 'Document updated successfully.')
                return redirect('documents:document_detail', slug=document.slug)
    else:
        form = DocumentForm(instance=document)
    
    return render(request, 'documents/document_form.html', {
        'form': form,
        'document': document,
        'title': f'Edit: {document.title}'
    })


@login_required
def document_download(request, slug):
    """
    Download a document file.
    """
    document = get_object_or_404(Document, slug=slug)
    
    # Check access permissions
    if document.access_level != Document.AccessLevel.PUBLIC:
        if not request.user.can_access_restricted:
            return HttpResponseForbidden("You don't have permission to download this document.")
    
    # Track download
    document.increment_download()
    DocumentAccessLog.objects.create(
        document=document,
        user=request.user,
        action=DocumentAccessLog.Action.DOWNLOAD,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Serve file
    response = FileResponse(document.file)
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(document.file.name)}"'
    response['Content-Type'] = document.mime_type
    response['Content-Length'] = document.file_size
    
    return response


@login_required
@permission_required('documents.delete_document')
def document_delete(request, slug):
    """
    Delete a document (soft delete).
    """
    document = get_object_or_404(Document, slug=slug)
    
    if request.method == 'POST':
        with transaction.atomic():
            # Soft delete
            document.is_published = False
            document.save()
            
            # Log deletion
            DocumentAccessLog.objects.create(
                document=document,
                user=request.user,
                action=DocumentAccessLog.Action.DELETE,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details='Document unpublished/deleted'
            )
            
            messages.success(request, 'Document has been removed.')
            return redirect('documents:document_list')
    
    return render(request, 'documents/document_confirm_delete.html', {
        'document': document,
        'title': f'Delete: {document.title}'
    })


@login_required
@permission_required('documents.change_document')
def document_publish(request, slug):
    """
    Publish a document.
    """
    document = get_object_or_404(Document, slug=slug)
    
    if request.method == 'POST':
        with transaction.atomic():
            document.is_published = True
            document.published_at = timezone.now()
            document.save()
            
            messages.success(request, 'Document has been published.')
            return redirect('documents:document_detail', slug=document.slug)
    
    return render(request, 'documents/document_confirm_publish.html', {
        'document': document,
        'title': f'Publish: {document.title}'
    })


@login_required
@permission_required('documents.change_document')
def document_unpublish(request, slug):
    """
    Unpublish a document.
    """
    document = get_object_or_404(Document, slug=slug)
    
    if request.method == 'POST':
        with transaction.atomic():
            document.is_published = False
            document.save()
            
            messages.success(request, 'Document has been unpublished.')
            return redirect('documents:document_detail', slug=document.slug)
    
    return render(request, 'documents/document_confirm_unpublish.html', {
        'document': document,
        'title': f'Unpublish: {document.title}'
    })


@login_required
def document_search(request):
    """
    Search documents.
    """
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = Document.objects.filter(
            is_published=True
        ).filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(keywords__icontains=query) |
            models.Q(act_number__icontains=query) |
            models.Q(bill_number__icontains=query)
        )[:50]
    
    return render(request, 'documents/document_search.html', {
        'results': results,
        'query': query,
        'title': 'Search Documents'
    })


@login_required
@permission_required('documents.view_document')
def document_stats(request):
    """
    Display document statistics.
    """
    stats = {
        'total_documents': Document.objects.count(),
        'published_documents': Document.objects.filter(is_published=True).count(),
        'unpublished_documents': Document.objects.filter(is_published=False).count(),
        'total_downloads': Document.objects.aggregate(
            total=models.Sum('download_count')
        )['total'] or 0,
        'total_views': Document.objects.aggregate(
            total=models.Sum('view_count')
        )['total'] or 0,
        'by_type': {},
        'by_year': {},
    }
    
    # Count by type
    for doc_type in Document.DocumentType.choices:
        count = Document.objects.filter(document_type=doc_type[0]).count()
        stats['by_type'][doc_type[1]] = count
    
    # Count by year
    years = Document.objects.values_list('year', flat=True).distinct().order_by('-year')
    for year in years:
        count = Document.objects.filter(year=year).count()
        stats['by_year'][year] = count
    
    return render(request, 'documents/document_stats.html', {
        'stats': stats,
        'title': 'Document Statistics'
    })


@login_required
def get_client_ip(request):
    """Get client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Import models for Q lookups
from django.db import models
