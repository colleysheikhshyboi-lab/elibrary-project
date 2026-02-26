"""
Admin configuration for document management.
"""

from django.contrib import admin
from .models import (
    Document, DocumentCategory, DocumentVersion, DocumentAccessLog,
    BillStage, BillStatus, Question, Answer, Committee, 
    CommitteeMeeting, CommitteeMember, Budget, Speech, Ordinance, Book
)
from .forms import DocumentForm


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
    add_form = DocumentForm
    form = DocumentForm
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
        'file_size', 'file_hash', 'download_count',
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


# =====================================================
# LEGISLATIVE TRACKING ADMIN (Feature 1)
# =====================================================

@admin.register(BillStage)
class BillStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'color')
    list_editable = ('order', 'color')
    search_fields = ('name', 'description')


@admin.register(BillStatus)
class BillStatusAdmin(admin.ModelAdmin):
    list_display = ('bill', 'status', 'stage', 'status_date', 'introduced_in')
    list_filter = ('status', 'stage', 'status_date')
    search_fields = ('bill__title', 'notes')
    date_hierarchy = 'status_date'


# =====================================================
# PARLIAMENTARY QUESTIONS ADMIN (Feature 2)
# =====================================================

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_number', 'member', 'question_type', 'ministry', 'date_raised', 'is_answered')
    list_filter = ('question_type', 'is_answered', 'is_admitted', 'date_raised')
    search_fields = ('question_number', 'subject', 'question_text')
    date_hierarchy = 'date_raised'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'minister', 'answering_ministry', 'answer_date')
    list_filter = ('answer_date', 'house')
    search_fields = ('question__question_number', 'answer_text')
    date_hierarchy = 'answer_date'


# =====================================================
# COMMITTEE SECTION ADMIN (Feature 3)
# =====================================================

@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'committee_type', 'ministry', 'is_active')
    list_filter = ('committee_type', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CommitteeMeeting)
class CommitteeMeetingAdmin(admin.ModelAdmin):
    list_display = ('committee', 'meeting_number', 'meeting_type', 'meeting_date', 'is_published')
    list_filter = ('meeting_type', 'is_published', 'meeting_date')
    search_fields = ('committee__name', 'agenda')
    date_hierarchy = 'meeting_date'


@admin.register(CommitteeMember)
class CommitteeMemberAdmin(admin.ModelAdmin):
    list_display = ('committee', 'member', 'role', 'from_date', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('committee__name', 'member__name')


# =====================================================
# BUDGET DOCUMENTS ADMIN (Feature 4)
# =====================================================

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'budget_type', 'fiscal_year', 'presented_date', 'is_approved')
    list_filter = ('budget_type', 'fiscal_year', 'is_approved')
    search_fields = ('title', 'ministry')
    date_hierarchy = 'presented_date'


# =====================================================
# MEMBER SPEECHES ADMIN (Feature 5)
# =====================================================

@admin.register(Speech)
class SpeechAdmin(admin.ModelAdmin):
    list_display = ('member', 'title', 'speech_type', 'session', 'debate_date', 'is_verified')
    list_filter = ('speech_type', 'is_verified', 'debate_date')
    search_fields = ('member__name', 'title', 'speech_text')
    date_hierarchy = 'debate_date'


# =====================================================
# ORDINANCE TRACKING ADMIN (Feature 6)
# =====================================================

@admin.register(Ordinance)
class OrdinanceAdmin(admin.ModelAdmin):
    list_display = ('ordinance_number', 'title', 'ministry', 'issued_date', 'status')
    list_filter = ('status', 'issued_date')
    search_fields = ('ordinance_number', 'title', 'description')
    date_hierarchy = 'issued_date'
    prepopulated_fields = {'slug': ('title',)}


# =====================================================
# BOOKS ADMIN
# =====================================================

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'publication_year', 'genre', 'is_available')
    list_filter = ('genre', 'is_available', 'is_reference_only', 'condition', 'publication_year')
    search_fields = ('author', 'document__title', 'isbn', 'accession_number')
    readonly_fields = ('catalog_date',)
    
    fieldsets = (
        ('Book Details', {
            'fields': ('document', 'author', 'co_authors')
        }),
        ('Publication Information', {
            'fields': ('isbn', 'publisher', 'publication_place', 'publication_year', 'edition', 'volume', 'pages')
        }),
        ('Classification', {
            'fields': ('genre', 'language')
        }),
        ('Physical Details', {
            'fields': ('binding', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Cataloging', {
            'fields': ('accession_number', 'barcode', 'shelf_location', 'catalog_date')
        }),
        ('Acquisition', {
            'fields': ('acquisition_date', 'acquisition_source', 'cost'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_available', 'is_reference_only', 'condition', 'notes')
        }),
    )
