"""
Admin configuration for document management.
"""

from django.contrib import admin
from .models import Document, DocumentCategory, DocumentVersion, DocumentAccessLog


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'document_count', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def document_count(self, obj):
        return obj.document_set.count()
    document_count.short_description = 'Documents'


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ('version', 'file', 'file_size', 'created_at')
    can_delete = False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'document_type', 'category', 
        'year', 'access_level', 'is_published',
        'uploaded_by', 'created_at', 'download_count'
    )
    list_filter = (
        'document_type', 'access_level', 'is_published',
        'category', 'year', 'created_at'
    )
    search_fields = ('title', 'description', 'keywords', 'act_number', 'bill_number')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    inlines = [DocumentVersionInline]
    
    readonly_fields = (
        'slug', 'file_size', 'file_hash', 'download_count',
        'view_count', 'created_at', 'updated_at', 'last_accessed_at'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'document_type', 'category')
        }),
        ('Description', {
            'fields': ('description', 'keywords')
        }),
        ('File Information', {
            'fields': ('file', 'file_size', 'mime_type')
        }),
        ('Version Control', {
            'fields': ('version', 'version_notes')
        }),
        ('Legislative Details', {
            'fields': (
                'act_number', 'bill_number', 'session', 'year',
                'date_enacted', 'effective_date', 'committee_name',
                'report_number'
            ),
            'classes': ('collapse',)
        }),
        ('Access Control', {
            'fields': ('access_level', 'is_published', 'published_at')
        }),
        ('Metadata', {
            'fields': ('language', 'pages', 'notes'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('uploaded_by', 'download_count', 'view_count', 
                      'created_at', 'updated_at', 'last_accessed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version', 'file_size', 'uploaded_by', 'created_at')
    list_filter = ('version', 'created_at')
    search_fields = ('document__title', 'changes')
    readonly_fields = ('document', 'version', 'file', 'file_size', 'created_at')


@admin.register(DocumentAccessLog)
class DocumentAccessLogAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('document__title', 'user__username', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('document', 'user', 'action', 'ip_address', 
                      'user_agent', 'timestamp', 'details')
