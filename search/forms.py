"""
Advanced search form for documents.
"""

from django import forms
from documents.models import Document, DocumentCategory


class AdvancedSearchForm(forms.Form):
    """
    Advanced search form with multiple filters.
    """
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search keywords...',
            'autocomplete': 'off'
        })
    )
    
    document_type = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    year = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    access_level = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    category = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date From'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date To'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Document type choices
        type_choices = [('', 'All Document Types')]
        type_choices.extend(Document.DocumentType.choices)
        self.fields['document_type'].choices = type_choices
        
        # Year choices
        from django.utils import timezone
        current_year = timezone.now().year
        year_choices = [('', 'All Years')]
        for year in range(current_year, current_year - 30, -1):
            year_choices.append((year, str(year)))
        self.fields['year'].choices = year_choices
        
        # Access level choices
        level_choices = [('', 'All Access Levels')]
        level_choices.extend(Document.AccessLevel.choices)
        self.fields['access_level'].choices = level_choices
        
        # Category choices
        category_choices = [('', 'All Categories')]
        categories = DocumentCategory.objects.filter(is_active=True)
        for cat in categories:
            category_choices.append((cat.slug, cat.name))
        self.fields['category'].choices = category_choices
