"""
Search app for advanced document search functionality.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from documents.models import Document, DocumentCategory
from documents.forms import DocumentSearchForm


@login_required
def search_view(request):
    """
    Advanced search view with multiple filters.
    """
    query = request.GET.get('q', '')
    results = []
    search_form = DocumentSearchForm(request.GET)
    
    # Get filter parameters
    author = request.GET.get('author', '')
    doc_type = request.GET.get('type', '')
    category = request.GET.get('category', '')
    year_from = request.GET.get('year_from', '')
    year_to = request.GET.get('year_to', '')
    committee = request.GET.get('committee', '')
    language = request.GET.get('language', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    access_level = request.GET.get('access', '')
    sort_by = request.GET.get('sort', 'newest')
    
    # Check if any filter is active
    has_filters = any([
        query, author, doc_type, category, year_from, year_to,
        committee, language, date_from, date_to, access_level
    ])
    
    if query or has_filters:
        results = Document.objects.filter(is_published=True)
        
        # Text search
        if query:
            results = results.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(keywords__icontains=query) |
                Q(act_number__icontains=query) |
                Q(bill_number__icontains=query) |
                Q(committee_name__icontains=query) |
                Q(book_details__author__icontains=query)
            )
        
        # Author search
        if author:
            results = results.filter(
                Q(uploaded_by__first_name__icontains=author) |
                Q(uploaded_by__last_name__icontains=author) |
                Q(uploaded_by__username__icontains=author) |
                Q(book_details__author__icontains=author)
            )
        
        # Document type filter
        if doc_type:
            results = results.filter(document_type=doc_type)
        
        # Category filter
        if category:
            results = results.filter(category__slug=category)
        
        # Year range filter
        if year_from:
            results = results.filter(year__gte=int(year_from))
        if year_to:
            results = results.filter(year__lte=int(year_to))
        
        # Committee filter
        if committee:
            results = results.filter(committee_name__icontains=committee)
        
        # Language filter
        if language:
            results = results.filter(language=language)
        
        # Date range filter
        if date_from:
            from django.utils.dateparse import parse_date
            parsed_date = parse_date(date_from)
            if parsed_date:
                results = results.filter(created_at__date__gte=parsed_date)
        if date_to:
            from django.utils.dateparse import parse_date
            parsed_date = parse_date(date_to)
            if parsed_date:
                results = results.filter(created_at__date__lte=parsed_date)
        
        # Access level filter
        if access_level:
            results = results.filter(access_level=access_level)
        
        # Apply sorting
        if sort_by == 'oldest':
            results = results.order_by('created_at')
        elif sort_by == 'title_asc':
            results = results.order_by('title')
        elif sort_by == 'title_desc':
            results = results.order_by('-title')
        elif sort_by == 'downloads':
            results = results.order_by('-download_count')
        elif sort_by == 'views':
            results = results.order_by('-view_count')
        else:
            results = results.order_by('-created_at')
        
        # Get total count before pagination
        total_count = results.count()
        
        # Pagination
        per_page = request.GET.get('per_page', 20)
        try:
            per_page = int(per_page)
            if per_page not in [10, 20, 50, 100]:
                per_page = 20
        except ValueError:
            per_page = 20
        
        paginator = Paginator(results, per_page)
        page = request.GET.get('page')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
    else:
        total_count = 0
        paginator = None
    
    # Get categories for filter
    categories = DocumentCategory.objects.filter(is_active=True)
    
    # Get document types with counts
    doc_types = []
    for doc_type_choice in Document.DocumentType.choices:
        count = Document.objects.filter(
            document_type=doc_type_choice[0],
            is_published=True
        ).count()
        doc_types.append((doc_type_choice[0], doc_type_choice[1], count))
    
    # Current filters for display
    current_filters = {
        'q': query,
        'author': author,
        'type': doc_type,
        'category': category,
        'year_from': year_from,
        'year_to': year_to,
        'committee': committee,
        'language': language,
        'date_from': date_from,
        'date_to': date_to,
        'access': access_level,
        'sort': sort_by,
    }
    
    return render(request, 'search/search.html', {
        'results': results,
        'query': query,
        'form': search_form,
        'categories': categories,
        'doc_types': doc_types,
        'current_filters': current_filters,
        'total_count': total_count if has_filters or query else 0,
        'title': 'Search Documents'
    })
