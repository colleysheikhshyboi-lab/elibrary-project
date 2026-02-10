"""
Forms for document management.
"""

from django import forms
from .models import Document, DocumentCategory
from django.core.validators import FileExtensionValidator


class DocumentCategoryForm(forms.ModelForm):
    """
    Form for creating/editing document categories.
    """
    
    class Meta:
        model = DocumentCategory
        fields = ['name', 'slug', 'description', 'icon', 'color', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category Name'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL Slug'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Icon Class (e.g., file-text)'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class DocumentForm(forms.ModelForm):
    """
    Form for creating/editing documents.
    """
    
    file = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.rtf,.jpg,.jpeg,.png,.tiff'
        }),
        validators=[FileExtensionValidator(
            allowed_extensions=[
                'pdf', 'doc', 'docx', 'xls', 'xlsx',
                'ppt', 'pptx', 'txt', 'rtf', 'jpg',
                'jpeg', 'png', 'tiff', 'tif', 'xml', 'json'
            ]
        )]
    )
    
    class Meta:
        model = Document
        fields = [
            'title', 'document_type', 'category', 'description',
            'keywords', 'file', 'version', 'version_notes',
            'act_number', 'bill_number', 'session', 'year',
            'date_enacted', 'effective_date', 'committee_name',
            'report_number', 'access_level', 'language', 'pages', 'notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document Title'
            }),
            'document_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief description of the document'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comma-separated keywords'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Version (e.g., 1.0)'
            }),
            'version_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes about this version'
            }),
            'act_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Act Number'
            }),
            'bill_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bill Number'
            }),
            'session': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parliamentary Session'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'date_enacted': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'effective_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'committee_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Committee Name'
            }),
            'report_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Report Number'
            }),
            'access_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'language': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Language (e.g., en)'
            }),
            'pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of Pages'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category optional
        self.fields['category'].required = False
        self.fields['date_enacted'].required = False
        self.fields['effective_date'].required = False
        self.fields['pages'].required = False


class DocumentSearchForm(forms.Form):
    """
    Form for document search.
    """
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search documents...',
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add document type choices
        type_choices = [('', 'All Types')]
        type_choices.extend(Document.DocumentType.choices)
        self.fields['document_type'].choices = type_choices
        
        # Add year choices
        from django.utils import timezone
        current_year = timezone.now().year
        year_choices = [('', 'All Years')]
        for year in range(current_year, current_year - 30, -1):
            year_choices.append((year, str(year)))
        self.fields['year'].choices = year_choices
        
        # Add access level choices
        level_choices = [('', 'All Levels')]
        level_choices.extend(Document.AccessLevel.choices)
        self.fields['access_level'].choices = level_choices


class BulkUploadForm(forms.Form):
    """
    Form for bulk document upload.
    """
    
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx'
        }),
        help_text='Select files to upload (one at a time)',
        required=False
    )
    document_type = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    category = forms.ModelChoiceField(
        queryset=DocumentCategory.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    access_level = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document_type'].choices = Document.DocumentType.choices
        self.fields['access_level'].choices = Document.AccessLevel.choices
