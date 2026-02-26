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
        BOOK = 'book', 'Book'
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


# =====================================================
# LEGISLATIVE TRACKING MODELS (Feature 1)
# =====================================================

class BillStage(models.Model):
    """
    Stages in the legislative process for tracking Bill progression.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Stage Name'
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
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Stage Order'
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Color Code'
    )
    icon = models.CharField(
        max_length=50,
        default='bi-circle',
        verbose_name='Icon Class'
    )
    
    class Meta:
        verbose_name = 'Bill Stage'
        verbose_name_plural = 'Bill Stages'
        ordering = ['order']
    
    def __str__(self):
        return self.name


class BillStatus(models.Model):
    """
    Track the status progression of Bills through the legislative process.
    """
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        INTRODUCED = 'introduced', 'Introduced'
        UNDER_REVIEW = 'under_review', 'Under Review'
        PASSED = 'passed', 'Passed'
        ASSENTED = 'assented', 'Assented by President'
        ACT = 'act', 'Enacted as Act'
        REJECTED = 'rejected', 'Rejected'
        WITHDRAWN = 'withdrawn', 'Withdrawn'
        LAPSED = 'lapsed', 'Lapsed'
    
    bill = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='bill_statuses',
        limit_choices_to={'document_type': 'bill'},
        verbose_name='Bill'
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        verbose_name='Status'
    )
    stage = models.ForeignKey(
        BillStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Legislative Stage'
    )
    status_date = models.DateField(
        verbose_name='Status Date'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )
    introduced_in = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Introduced In (House)'
    )
    introduced_by = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Introduced By (Minister/Member)'
    )
    motion_text = models.TextField(
        blank=True,
        verbose_name='Motion Text'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Bill Status'
        verbose_name_plural = 'Bill Statuses'
        ordering = ['-status_date']
    
    def __str__(self):
        return f"{self.bill.title} - {self.get_status_display()}"


# =====================================================
# PARLIAMENTARY QUESTIONS MODELS (Feature 2)
# =====================================================

class Question(models.Model):
    """
    Parliamentary Questions raised in the parliament.
    """
    class QuestionType(models.TextChoices):
        ORAL = 'oral', 'Oral Question'
        WRITTEN = 'written', 'Written Question'
        STARRED = 'starred', 'Starred Question'
        UNSTARRED = 'unstarred', 'Unstarred Question'
        SHORT_NOTICE = 'short_notice', 'Short Notice Question'
    
    class Priority(models.TextChoices):
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'
    
    question_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Question Number'
    )
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        verbose_name='Question Type'
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name='Priority'
    )
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Member'
    )
    ministry = models.CharField(
        max_length=200,
        verbose_name='Ministry/Department'
    )
    subject = models.CharField(
        max_length=500,
        verbose_name='Question Subject'
    )
    question_text = models.TextField(
        verbose_name='Question Text'
    )
    session = models.CharField(
        max_length=50,
        verbose_name='Parliamentary Session'
    )
    house = models.CharField(
        max_length=50,
        choices=[
            ('lok_sabha', 'Lok Sabha'),
            ('rajya_sabha', 'Rajya Sabha'),
            ('both', 'Both Houses'),
        ],
        verbose_name='House'
    )
    date_raised = models.DateField(
        verbose_name='Date Raised'
    )
    answering_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Answering Date'
    )
    is_answered = models.BooleanField(
        default=False,
        verbose_name='Is Answered'
    )
    is_admitted = models.BooleanField(
        default=False,
        verbose_name='Is Admitted'
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Tags',
        help_text='Comma-separated keywords'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Parliamentary Question'
        verbose_name_plural = 'Parliamentary Questions'
        ordering = ['-date_raised']
        permissions = [
            ('approve_question', 'Can approve questions'),
        ]
    
    def __str__(self):
        return f"Q.No. {self.question_number} - {self.subject[:50]}"


class Answer(models.Model):
    """
    Answers to Parliamentary Questions.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Question'
    )
    answer_text = models.TextField(
        verbose_name='Answer Text'
    )
    minister = models.CharField(
        max_length=200,
        verbose_name='Answering Minister'
    )
    answering_ministry = models.CharField(
        max_length=200,
        verbose_name='Ministry'
    )
    answer_date = models.DateField(
        verbose_name='Answer Date'
    )
    house = models.CharField(
        max_length=50,
        verbose_name='House'
    )
    hansard_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Hansard Reference'
    )
    is_final = models.BooleanField(
        default=True,
        verbose_name='Is Final Answer'
    )
    supplementary_questions = models.TextField(
        blank=True,
        verbose_name='Supplementary Questions'
    )
    linked_documents = models.ManyToManyField(
        Document,
        blank=True,
        related_name='related_answers',
        verbose_name='Linked Documents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['-answer_date']
    
    def __str__(self):
        return f"Answer to Q.No. {self.question.question_number}"


# =====================================================
# COMMITTEE SECTION MODELS (Feature 3)
# =====================================================

class Committee(models.Model):
    """
    Parliamentary Committees.
    """
    class CommitteeType(models.TextChoices):
        STANDING = 'standing', 'Standing Committee'
        SELECT = 'select', 'Select Committee'
        JOINT = 'joint', 'Joint Committee'
        ADHOC = 'adhoc', 'Ad-hoc Committee'
        BUSINESS = 'business', 'Business Advisory Committee'
        PUBLIC_ACCOUNTS = 'public_accounts', 'Public Accounts Committee'
        ESTIMATES = 'estimates', 'Estimates Committee'
        PETITIONS = 'petitions', 'Petitions Committee'
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Committee Name'
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        verbose_name='URL Slug'
    )
    committee_type = models.CharField(
        max_length=30,
        choices=CommitteeType.choices,
        verbose_name='Committee Type'
    )
    description = models.TextField(
        verbose_name='Description'
    )
    ministry = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Related Ministry'
    )
    year_formed = models.PositiveIntegerField(
        verbose_name='Year Formed'
    )
    term_start = models.DateField(
        null=True,
        blank=True,
        verbose_name='Current Term Start'
    )
    term_end = models.DateField(
        null=True,
        blank=True,
        verbose_name='Current Term End'
    )
    chair_person = models.ForeignKey(
        'members.Member',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='committee_chairs',
        verbose_name='Chairperson'
    )
    vice_chair_person = models.ForeignKey(
        'members.Member',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='committee_vice_chairs',
        verbose_name='Vice Chairperson'
    )
    secretary = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Secretary'
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name='Contact Email'
    )
    contact_phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Contact Phone'
    )
    meeting_frequency = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Meeting Frequency'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active'
    )
    reports = models.ManyToManyField(
        Document,
        blank=True,
        related_name='committee_reports',
        verbose_name='Committee Reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Committee'
        verbose_name_plural = 'Committees'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CommitteeMeeting(models.Model):
    """
    Committee Meeting schedules and minutes.
    """
    class MeetingType(models.TextChoices):
        ORGANIZATIONAL = 'organizational', 'Organizational Meeting'
        EXAMINATION = 'examination', 'Examination Meeting'
        HEARING = 'hearing', 'Public Hearing'
        DELIBERATION = 'deliberation', 'Deliberation Meeting'
        Briefing = 'briefing', 'Briefing'
    
    committee = models.ForeignKey(
        Committee,
        on_delete=models.CASCADE,
        related_name='meetings',
        verbose_name='Committee'
    )
    meeting_number = models.CharField(
        max_length=20,
        verbose_name='Meeting Number'
    )
    meeting_type = models.CharField(
        max_length=30,
        choices=MeetingType.choices,
        verbose_name='Meeting Type'
    )
    meeting_date = models.DateTimeField(
        verbose_name='Meeting Date & Time'
    )
    venue = models.CharField(
        max_length=200,
        verbose_name='Venue'
    )
    agenda = models.TextField(
        verbose_name='Agenda'
    )
    minutes = models.TextField(
        blank=True,
        verbose_name='Minutes'
    )
    witnesses = models.TextField(
        blank=True,
        verbose_name='Witnesses/Presentations'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Is Published'
    )
    presentation_documents = models.ManyToManyField(
        Document,
        blank=True,
        related_name='meeting_presentations',
        verbose_name='Presentation Documents'
    )
    minutes_document = models.FileField(
        upload_to='committees/minutes/',
        null=True,
        blank=True,
        verbose_name='Minutes Document'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Committee Meeting'
        verbose_name_plural = 'Committee Meetings'
        ordering = ['-meeting_date']
    
    def __str__(self):
        return f"{self.committee.name} - Meeting #{self.meeting_number}"


class CommitteeMember(models.Model):
    """
    Committee Membership.
    """
    class Role(models.TextChoices):
        CHAIR = 'chair', 'Chairperson'
        VICE_CHAIR = 'vice_chair', 'Vice Chairperson'
        MEMBER = 'member', 'Member'
        CONVENOR = 'convenor', 'Convenor'
        SECRETARY = 'secretary', 'Secretary'
    
    committee = models.ForeignKey(
        Committee,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Committee'
    )
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='committee_memberships',
        verbose_name='Member'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
        verbose_name='Role'
    )
    from_date = models.DateField(
        verbose_name='From Date'
    )
    to_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='To Date'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active Member'
    )
    
    class Meta:
        verbose_name = 'Committee Member'
        verbose_name_plural = 'Committee Members'
        unique_together = ['committee', 'member', 'from_date']
    
    def __str__(self):
        return f"{self.member.name} - {self.committee.name} ({self.get_role_display()})"


# =====================================================
# BUDGET DOCUMENTS MODELS (Feature 4)
# =====================================================

class Budget(models.Model):
    """
    Budget documents for parliamentary sessions.
    """
    class BudgetType(models.TextChoices):
        UNION_BUDGET = 'union', 'Union Budget'
        STATE_BUDGET = 'state', 'State Budget'
        SUPPLEMENTARY = 'supplementary', 'Supplementary Budget'
        DEMAND_GRANT = 'demand', 'Demand for Grants'
        FINANCE_BILL = 'finance_bill', 'Finance Bill'
        BUDGET_AT_A_GLANCE = 'glance', 'Budget at a Glance'
        MEMORANDUM = 'memorandum', 'Memorandum'
    
    title = models.CharField(
        max_length=500,
        verbose_name='Budget Title'
    )
    slug = models.SlugField(
        max_length=500,
        unique=True,
        verbose_name='URL Slug'
    )
    budget_type = models.CharField(
        max_length=20,
        choices=BudgetType.choices,
        verbose_name='Budget Type'
    )
    fiscal_year = models.CharField(
        max_length=10,
        verbose_name='Fiscal Year'
    )
    ministry = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Ministry/Department'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='budget_documents',
        verbose_name='Budget Document'
    )
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Total Amount (in Crores)'
    )
    session = models.CharField(
        max_length=50,
        verbose_name='Parliamentary Session'
    )
    presented_date = models.DateField(
        verbose_name='Date Presented'
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name='Approved by Parliament'
    )
    approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Approval Date'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        ordering = ['-presented_date']
    
    def __str__(self):
        return f"{self.title} ({self.fiscal_year})"


# =====================================================
# MEMBER SPEECHES MODELS (Feature 5)
# =====================================================

class Speech(models.Model):
    """
    Speeches by Members of Parliament in Hansards.
    """
    class SpeechType(models.TextChoices):
        DEBATE = 'debate', 'Debate Speech'
        MOTION = 'motion', 'Motion Speech'
        QUESTION = 'question', 'Question Speech'
        STATEMENT = 'statement', 'Statement'
        INTERJECTION = 'interjection', 'Interjection'
        WRITTEN_SPEECH = 'written', 'Written Speech'
    
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='speeches',
        verbose_name='Member'
    )
    speech_type = models.CharField(
        max_length=20,
        choices=SpeechType.choices,
        verbose_name='Speech Type'
    )
    title = models.CharField(
        max_length=500,
        verbose_name='Speech Title'
    )
    hansard = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        limit_choices_to={'document_type': 'hansard'},
        related_name='speeches',
        verbose_name='Hansard Reference'
    )
    speech_text = models.TextField(
        verbose_name='Speech Text'
    )
    session = models.CharField(
        max_length=50,
        verbose_name='Parliamentary Session'
    )
    house = models.CharField(
        max_length=50,
        verbose_name='House'
    )
    debate_date = models.DateField(
        verbose_name='Debate Date'
    )
    page_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Page Number'
    )
    column_start = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Column Start'
    )
    column_end = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Column End'
    )
    ministry = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Ministry/Subject'
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Tags'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Is Verified'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Speech'
        verbose_name_plural = 'Speeches'
        ordering = ['-debate_date']
        permissions = [
            ('verify_speech', 'Can verify speeches'),
        ]
    
    def __str__(self):
        return f"{self.member.name} - {self.title[:50]}"


# =====================================================
# ORDINANCE TRACKING MODELS (Feature 6)
# =====================================================

class Ordinance(models.Model):
    """
    Ordinanaces issued by the President/Government.
    """
    class Status(models.TextChoices):
        ISSUED = 'issued', 'Issued'
        REPEALED = 'repealed', 'Repealed'
        EXPIRED = 'expired', 'Expired'
        REPLACED = 'replaced', 'Replaced by Act'
        LAPSED = 'lapsed', 'Lapsed'
    
    ordinance_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Ordinance Number'
    )
    title = models.CharField(
        max_length=500,
        verbose_name='Ordinance Title'
    )
    slug = models.SlugField(
        max_length=500,
        unique=True,
        verbose_name='URL Slug'
    )
    short_title = models.CharField(
        max_length=200,
        verbose_name='Short Title'
    )
    description = models.TextField(
        verbose_name='Description'
    )
    ministry = models.CharField(
        max_length=200,
        verbose_name='Issuing Ministry'
    )
    issuing_authority = models.CharField(
        max_length=200,
        verbose_name='Issuing Authority'
    )
    
    # Dates
    issued_date = models.DateField(
        verbose_name='Issue Date'
    )
    notification_number = models.CharField(
        max_length=50,
        verbose_name='Notification Number'
    )
    gazette_reference = models.CharField(
        max_length=100,
        verbose_name='Gazette Reference'
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ISSUED,
        verbose_name='Current Status'
    )
    repealed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Repealed Date'
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Expiry Date'
    )
    replacement_act = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'document_type': 'act'},
        related_name='replaced_ordinances',
        verbose_name='Replaced by Act'
    )
    
    # Related documents
    ordinance_document = models.FileField(
        upload_to='ordinances/',
        verbose_name='Ordinance Document'
    )
    linked_documents = models.ManyToManyField(
        Document,
        blank=True,
        related_name='related_ordinances',
        verbose_name='Linked Documents'
    )
    
    # Parliament consideration
    laid_before_parliament = models.BooleanField(
        default=False,
        verbose_name='Laid Before Parliament'
    )
    parliament_approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Parliament Approval Date'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Additional Notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ordinance'
        verbose_name_plural = 'Ordinances'
        ordering = ['-issued_date']
        permissions = [
            ('manage_ordinance', 'Can manage ordinances'),
        ]
    
    def __str__(self):
        return f"Ordinance {self.ordinance_number} - {self.title[:50]}"
    
    @property
    def is_active(self):
        """Check if ordinance is still active."""
        return self.status == self.Status.ISSUED and (
            self.expiry_date is None or self.expiry_date >= timezone.now().date()
        )


# =====================================================
# BOOKS MODELS
# =====================================================

class Book(models.Model):
    """
    Books in the parliamentary library collection.
    """
    class Genre(models.TextChoices):
        CONSTITUTIONAL_LAW = 'constitutional_law', 'Constitutional Law'
        PARLIAMENTARY_PROCEDURE = 'parliamentary_procedure', 'Parliamentary Procedure'
        LEGISLATIVE_STUDIES = 'legislative_studies', 'Legislative Studies'
        PUBLIC_POLICY = 'public_policy', 'Public Policy'
        GOVERNANCE = 'governance', 'Governance'
        DEMOCRACY = 'democracy', 'Democracy & Elections'
        BIOGRAPHY = 'biography', 'Biography/Memoir'
        HISTORY = 'history', 'History'
        REFERENCE = 'reference', 'Reference'
        OTHER = 'other', 'Other'
    
    # Link to Document for file storage
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='book_details',
        verbose_name='Associated Document'
    )
    
    # Book-specific fields
    author = models.CharField(
        max_length=300,
        verbose_name='Author(s)'
    )
    co_authors = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Co-Author(s)'
    )
    isbn = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='ISBN'
    )
    publisher = models.CharField(
        max_length=200,
        verbose_name='Publisher'
    )
    publication_place = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Publication Place'
    )
    publication_year = models.PositiveIntegerField(
        verbose_name='Publication Year'
    )
    edition = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Edition'
    )
    volume = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Volume'
    )
    pages = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Number of Pages'
    )
    genre = models.CharField(
        max_length=30,
        choices=Genre.choices,
        default=Genre.OTHER,
        verbose_name='Genre/Category'
    )
    language = models.CharField(
        max_length=20,
        default='en',
        verbose_name='Language'
    )
    
    # Binding and physical details
    binding = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Binding Type',
        help_text='e.g., Hardcover, Paperback'
    )
    dimensions = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Dimensions'
    )
    
    # Acquisition details
    accession_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Accession Number'
    )
    acquisition_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Acquisition Date'
    )
    acquisition_source = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Acquisition Source'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Cost'
    )
    
    # Cataloging
    catalog_date = models.DateField(
        auto_now_add=True,
        verbose_name='Catalog Date'
    )
    shelf_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Shelf Location'
    )
    barcode = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Barcode'
    )
    
    # Status
    is_available = models.BooleanField(
        default=True,
        verbose_name='Available for Borrowing'
    )
    is_reference_only = models.BooleanField(
        default=False,
        verbose_name='Reference Only'
    )
    condition = models.CharField(
        max_length=50,
        choices=[
            ('new', 'New'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        default='new',
        verbose_name='Condition'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )
    
    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['author', 'publication_year']
        permissions = [
            ('manage_books', 'Can manage library books'),
        ]
    
    def __str__(self):
        return f"{self.author} - {self.document.title}"
    
    @property
    def title(self):
        """Get the book title from the linked document."""
        return self.document.title
    
    @property
    def full_citation(self):
        """Generate full citation for the book."""
        citation = f"{self.author}. ({self.publication_year}). "
        citation += f"{self.document.title}"
        if self.edition:
            citation += f" ({self.edition} ed.)"
        citation += f". {self.publisher}."
        return citation
