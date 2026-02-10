"""
Search app for advanced document search functionality.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from documents.models import Document
from .forms import AdvancedSearchForm


@login_required
def search_view(request):
    """
    Advanced search view with multiple filters.
    """
    query = request.GET.get('q', '')
    results = []
    form = AdvancedSearchForm(request.GET)
    
    if query or form.is_valid():
        results = Document.objects.filter(is_published=True)
        
        # Text search
        if query:
            results = results.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(keywords__icontains=query) |
                Q(act_number__icontains=query) |
                Q(bill_number__icontains=query) |
                Q(committee_name__icontains=query)
            )
        
        # Apply filters
        if form.cleaned_data.get('document_type'):
            results = results.filter(
                document_type=form.cleaned_data['document_type']
            )
        
        if form.cleaned_data.get('year'):
            results = results.filter(year=form.cleaned_data['year'])
        
        if form.cleaned_data.get('access_level'):
            results = results.filter(
                access_level=form.cleaned_data['access_level']
            )
        
        if form.cleaned_data.get('category'):
            results = results.filter(
                category__slug=form.cleaned_data['category']
            )
        
        # Order results
        results = results.order_by('-created_at')[:100]
    
    return render(request, 'search/search.html', {
        'results': results,
        'query': query,
        'form': form,
        'title': 'Search Documents'
    })
