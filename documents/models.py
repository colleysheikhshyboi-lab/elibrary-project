"""
Document models for the e-Library system.
Handles all parliamentary documents including Acts, Bills, Hansards, etc.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os

User = get_user_model()


def document_upload_path(instance, filename):
    """Generate upload path for document files."""
    date_path = timezone.now().strftime('%Y/%m')
    document_type = instance.document_type.lower().replace(' ', '_')
    return f'documents/{date_path}/{document_type}_{instance.id}_{filename}'


class DocumentCategory(models.Model):
    """
    Categories for organizing parliamentary documents.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Category Name'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='URL Slug'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    icon = models.CharField(
        max_length=50,
        default='file-text',
        verbose_name='Icon Class'
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Color Code'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Display Order'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Document Category'
        verbose_name_plural = 'Document Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Document(models.Model):
    """
    Main document model for all parliamentary documents.
    """
    
    class DocumentType(models.TextChoices):
        ACT = 'act', 'Act of Parliament'
        BILL = 'bill', 'Bill'
        AMENDMENT = 'amendment', 'Amendment'
        HANSARD = 'hansard', 'Hansard'
        COMMITTEE_REPORT = 'committee_report', 'Committee Report'
        PARLIAMENTARY_JOURNAL = 'journal', 'Parliamentary Journal'
        GAZETTE = 'gazette', 'Gazette'
        RESEARCH_DOCUMENT = 'research', 'Research Document'
        CONTRACT = 'contract', 'Contract/Agreement'
        POLICY = 'policy', 'Policy Document'
        OTHER = 'other', 'Other'
    
    class AccessLevel(models.TextChoices):
        PUBLIC = 'public', 'Public'
        RESTRICTED = 'restricted', 'Restricted'
        CONFIDENTIAL = 'confidential', 'Confidential'
        CLASSIFIED = 'classified', 'Classified'
    
    # Basic Information
    title = models.CharField(
        max_length=500,
        verbose_name='Document Title'
    )
    slug = models.SlugField(
        max_length=500,
        unique=True,
        verbose_name='URL Slug'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
        verbose_name='Document Type'
    )
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Category'
    )
    
    # Description and Metadata
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    keywords = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Keywords',
        help_text='Comma-separated keywords for search'
    )
    
    # File Information
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(
            allowed_extensions=[
                'pdf', 'doc', 'docx', 'xls', 'xlsx',
                'ppt', 'pptx', 'txt', 'rtf', 'jpg',
                'jpeg', 'png', 'tiff', 'tif', 'xml', 'json'
            ]
        )],
        verbose_name='Document File'
    )
    file_size = models.BigIntegerField(
        default=0,
        verbose_name='File Size (bytes)'
    )
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='File Hash (SHA-256)'
    )
    mime_type = models.CharField(
        max_length=100,
        default='application/octet-stream',
        verbose_name='MIME Type'
    )
    
    # Version Control
    version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name='Version'
    )
    version_notes = models.TextField(
        blank=True,
        verbose_name='Version Notes'
    )
    
    # Legislative Information
    act_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Act Number'
    )
    bill_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Bill Number'
    )
    session = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Parliamentary Session'
    )
    year = models.PositiveIntegerField(
        default=timezone.now().year,
        verbose_name='Year'
    )
    date_enacted = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date Enacted/Published'
    )
    effective_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Effective Date'
    )
    
    # Committee Information
    committee_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Committee Name'
    )
    report_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Report Number'
    )
    
    # Access Control
    access_level = models.CharField(
        max_length=20,
        choices=AccessLevel.choices,
        default=AccessLevel.PUBLIC,
        verbose_name='Access Level'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Is Published'
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Published Date'
    )
    
    # Audit Trail
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name='Uploaded By'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Last Accessed'
    )
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Download Count'
    )
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='View Count'
    )
    
    # Metadata
    language = models.CharField(
        max_length=10,
        default='en',
        verbose_name='Language'
    )
    pages = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Number of Pages'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Additional Notes'
    )
    
    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
        permissions = [
            ('view_restricted', 'Can view restricted documents'),
            ('view_confidential', 'Can view confidential documents'),
            ('view_classified', 'Can view classified documents'),
            ('approve_document', 'Can approve documents for publication'),
            ('bulk_upload', 'Can bulk upload documents'),
            ('export_document', 'Can export documents'),
        ]
        indexes = [
            models.Index(fields=['document_type', 'year']),
            models.Index(fields=['access_level', 'is_published']),
            models.Index(fields=['uploaded_by', 'created_at']),
            models.Index(fields=['title', 'slug']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"
    
    def save(self, *args, **kwargs):
        # Set file size on save
        if self.file and not self.file_size:
            self.file_size = self.file.size
        
        # Generate slug if not exists
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title[:100])
            slug = base_slug
            counter = 1
            while Document.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Set published date
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_restricted(self):
        """Check if document has restricted access."""
        return self.access_level in [
            self.AccessLevel.RESTRICTED,
            self.AccessLevel.CONFIDENTIAL,
            self.AccessLevel.CLASSIFIED
        ]
    
    def get_file_extension(self):
        """Get file extension."""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''
    
    def get_file_size_mb(self):
        """Get file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)
    
    def increment_download(self):
        """Increment download counter."""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def increment_view(self):
        """Increment view counter."""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class DocumentVersion(models.Model):
    """
    Track document version history.
    """
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='Document'
    )
    version = models.CharField(
        max_length=20,
        verbose_name='Version Number'
    )
    file = models.FileField(
        upload_to=document_upload_path,
        verbose_name='Version File'
    )
    file_size = models.BigIntegerField(
        default=0,
        verbose_name='File Size (bytes)'
    )
    changes = models.TextField(
        blank=True,
        verbose_name='Change Notes'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Uploaded By'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Document Version'
        verbose_name_plural = 'Document Versions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.document.title} - v{self.version}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class DocumentAccessLog(models.Model):
    """
    Log document access for audit trail.
    """
    
    class Action(models.TextChoices):
        VIEW = 'view', 'View'
        DOWNLOAD = 'download', 'Download'
        PRINT = 'print', 'Print'
        SHARE = 'share', 'Share'
        EDIT = 'edit', 'Edit'
        DELETE = 'delete', 'Delete'
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_logs',
        verbose_name='Document'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='User'
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name='Action'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Timestamp'
    )
    details = models.TextField(
        blank=True,
        verbose_name='Additional Details'
    )
    
    class Meta:
        verbose_name = 'Document Access Log'
        verbose_name_plural = 'Document Access Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Anonymous'
        return f"{user_name} {self.action} {self.document.title} at {self.timestamp}"
