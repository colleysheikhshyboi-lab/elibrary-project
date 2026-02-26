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
            'title', 'slug', 'document_type', 'category', 'description',
            'keywords', 'file', 'version', 'version_notes',
            'act_number', 'bill_number', 'session', 'year',
            'date_enacted', 'effective_date', 'committee_name',
            'report_number', 'access_level', 'is_published', 'published_at',
            'language', 'pages', 'notes', 'uploaded_by'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document Title'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL Slug (auto-generated if empty)'
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
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'published_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'uploaded_by': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
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
    Form for document search with advanced filters.
    """
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search documents by title, description, keywords...',
            'autocomplete': 'off'
        })
    )
    
    # Author search (for both Document uploader and Book author)
    author = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by author name...',
            'autocomplete': 'off'
        })
    )
    
    document_type = forms.ChoiceField(
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
    
    # Year range
    year_from = forms.ChoiceField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'From',
            'min': '1900'
        }),
        label='Year From'
    )
    
    year_to = forms.ChoiceField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'To',
            'min': '1900'
        }),
        label='Year To'
    )
    
    # Committee / Department filter
    committee = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by committee/department...'
        })
    )
    
    # Language filter
    language = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # Date uploaded range
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date Uploaded From'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date Uploaded To'
    )
    
    # Sort options
    sort_by = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        choices=[
            ('', 'Newest First'),
            ('oldest', 'Oldest First'),
            ('title_asc', 'Title A-Z'),
            ('title_desc', 'Title Z-A'),
            ('downloads', 'Most Downloaded'),
            ('views', 'Most Viewed'),
        ],
        initial='newest'
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
        type_choices = [('', 'All Document Types')]
        type_choices.extend(Document.DocumentType.choices)
        self.fields['document_type'].choices = type_choices
        
        # Add year choices
        from django.utils import timezone
        current_year = timezone.now().year
        year_choices = [('', 'Any Year')]
        for year in range(current_year, current_year - 50, -1):
            year_choices.append((year, str(year)))
        self.fields['year_from'].choices = year_choices
        self.fields['year_to'].choices = year_choices
        
        # Add language choices
        language_choices = [('', 'All Languages')]
        language_choices.extend([
            ('en', 'English'),
            ('fr', 'French'),
            ('ar', 'Arabic'),
            ('pt', 'Portuguese'),
            ('other', 'Other'),
        ])
        self.fields['language'].choices = language_choices
        
        # Add access level choices
        level_choices = [('', 'All Access Levels')]
        level_choices.extend(Document.AccessLevel.choices)
        self.fields['access_level'].choices = level_choices
        
        # Add category choices
        category_choices = [('', 'All Categories')]
        categories = DocumentCategory.objects.filter(is_active=True)
        for cat in categories:
            category_choices.append((cat.slug, cat.name))
        self.fields['category'].choices = category_choices


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
