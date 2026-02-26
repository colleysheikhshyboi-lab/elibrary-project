"""
Views for document management.
Handles document upload, viewing, downloading, and search.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.db import transaction, models
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods
from django.template.defaultfilters import filesizeformat
from .models import (
    Document, DocumentCategory, DocumentVersion, DocumentAccessLog,
    BillStage, BillStatus, Question, Answer, Committee,
    CommitteeMeeting, CommitteeMember, Budget, Speech, Ordinance, Book
)
from .forms import DocumentForm, DocumentSearchForm
import os


@login_required
def document_list(request):
    """
    Display list of documents with advanced filtering and search.
    """
    # Show all documents (published + unpublished) for users who can upload
    # Otherwise only show published documents
    if request.user.can_upload:
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(is_published=True)
    
    # Initialize search form
    search_form = DocumentSearchForm(request.GET)
    
    # Get filter parameters from GET request
    query = request.GET.get('q', '')
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
    
    # Text search (title, description, keywords)
    if query:
        documents = documents.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(keywords__icontains=query) |
            models.Q(act_number__icontains=query) |
            models.Q(bill_number__icontains=query) |
            models.Q(committee_name__icontains=query) |
            # Also search in Book author
            models.Q(book_details__author__icontains=query)
        )
    
    # Author search (uploader or Book author)
    if author:
        documents = documents.filter(
            models.Q(uploaded_by__first_name__icontains=author) |
            models.Q(uploaded_by__last_name__icontains=author) |
            models.Q(uploaded_by__username__icontains=author) |
            models.Q(book_details__author__icontains=author)
        )
    
    # Document type filter
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    # Category filter
    if category:
        documents = documents.filter(category__slug=category)
    
    # Year range filter
    if year_from:
        documents = documents.filter(year__gte=int(year_from))
    if year_to:
        documents = documents.filter(year__lte=int(year_to))
    
    # Committee / Department filter
    if committee:
        documents = documents.filter(committee_name__icontains=committee)
    
    # Language filter
    if language:
        documents = documents.filter(language=language)
    
    # Date uploaded range filter
    if date_from:
        from django.utils.dateparse import parse_date
        parsed_date = parse_date(date_from)
        if parsed_date:
            documents = documents.filter(created_at__date__gte=parsed_date)
    if date_to:
        from django.utils.dateparse import parse_date
        parsed_date = parse_date(date_to)
        if parsed_date:
            documents = documents.filter(created_at__date__lte=parsed_date)
    
    # Access level filter
    if access_level:
        documents = documents.filter(access_level=access_level)
    
    # Apply sorting
    if sort_by == 'oldest':
        documents = documents.order_by('created_at')
    elif sort_by == 'title_asc':
        documents = documents.order_by('title')
    elif sort_by == 'title_desc':
        documents = documents.order_by('-title')
    elif sort_by == 'downloads':
        documents = documents.order_by('-download_count')
    elif sort_by == 'views':
        documents = documents.order_by('-view_count')
    else:
        # Default: newest first
        documents = documents.order_by('-created_at')
    
    # Pagination
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except ValueError:
        per_page = 20
    
    paginator = Paginator(documents, per_page)
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
    
    # Get unique years for year filter
    years = Document.objects.values_list('year', flat=True).distinct().order_by('-year')
    
    return render(request, 'documents/document_list.html', {
        'documents': documents,
        'categories': categories,
        'doc_types': doc_types,
        'years': years,
        'search_form': search_form,
        'title': 'Document Library',
        'current_filters': {
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

# =====================================================
# LEGISLATIVE TRACKING VIEWS (Feature 1)
# =====================================================

@login_required
def bill_list(request):
    """
    Display list of Bills with their current status.
    """
    bills = Document.objects.filter(
        document_type='bill',
        is_published=True
    ).prefetch_related('bill_statuses')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bills = bills.filter(bill_statuses__status=status)
    
    # Search
    query = request.GET.get('q')
    if query:
        bills = bills.filter(
            models.Q(title__icontains=query) |
            models.Q(bill_number__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(bills, 20)
    page = request.GET.get('page')
    try:
        bills = paginator.page(page)
    except PageNotAnInteger:
        bills = paginator.page(1)
    except EmptyPage:
        bills = paginator.page(paginator.num_pages)
    
    return render(request, 'documents/bill_list.html', {
        'bills': bills,
        'title': 'Legislative Tracking - Bills'
    })


@login_required
def bill_detail(request, slug):
    """
    Display Bill details with status timeline.
    """
    bill = get_object_or_404(
        Document,
        slug=slug,
        document_type='bill'
    )
    
    # Get status history
    statuses = bill.bill_statuses.all().order_by('status_date')
    
    return render(request, 'documents/bill_detail.html', {
        'bill': bill,
        'statuses': statuses,
        'title': bill.title
    })


# =====================================================
# PARLIAMENTARY QUESTIONS VIEWS (Feature 2)
# =====================================================

@login_required
def question_list(request):
    """
    Display list of Parliamentary Questions.
    """
    questions = Question.objects.all()
    
    # Filters
    q_type = request.GET.get('type')
    if q_type:
        questions = questions.filter(question_type=q_type)
    
    is_answered = request.GET.get('answered')
    if is_answered:
        questions = questions.filter(is_answered=(is_answered == 'true'))
    
    member_id = request.GET.get('member')
    if member_id:
        questions = questions.filter(member_id=member_id)
    
    # Search
    query = request.GET.get('q')
    if query:
        questions = questions.filter(
            models.Q(subject__icontains=query) |
            models.Q(question_number__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(questions, 20)
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)
    
    return render(request, 'documents/question_list.html', {
        'questions': questions,
        'title': 'Parliamentary Questions'
    })


@login_required
def question_detail(request, pk):
    """
    Display Question details with Answer.
    """
    question = get_object_or_404(Question, pk=pk)
    answers = question.answers.all()
    
    return render(request, 'documents/question_detail.html', {
        'question': question,
        'answers': answers,
        'title': f"Q.No. {question.question_number}"
    })


# =====================================================
# COMMITTEE SECTION VIEWS (Feature 3)
# =====================================================

@login_required
def committee_list(request):
    """
    Display list of Parliamentary Committees.
    """
    committees = Committee.objects.all()
    
    # Filter by type
    c_type = request.GET.get('type')
    if c_type:
        committees = committees.filter(committee_type=c_type)
    
    # Filter active only
    active_only = request.GET.get('active')
    if active_only == 'true':
        committees = committees.filter(is_active=True)
    
    return render(request, 'documents/committee_list.html', {
        'committees': committees,
        'title': 'Parliamentary Committees'
    })


@login_required
def committee_detail(request, slug):
    """
    Display Committee details with members and meetings.
    """
    committee = get_object_or_404(Committee, slug=slug)
    members = committee.members.filter(is_active=True)
    meetings = committee.meetings.filter(
        is_published=True
    ).order_by('-meeting_date')[:10]
    
    return render(request, 'documents/committee_detail.html', {
        'committee': committee,
        'members': members,
        'meetings': meetings,
        'title': committee.name
    })


@login_required
def committee_meeting_detail(request, committee_slug, meeting_id):
    """
    Display Committee Meeting details.
    """
    meeting = get_object_or_404(
        CommitteeMeeting,
        committee__slug=committee_slug,
        id=meeting_id
    )
    
    return render(request, 'documents/committee_meeting_detail.html', {
        'meeting': meeting,
        'title': f"{meeting.committee.name} - Meeting #{meeting.meeting_number}"
    })


# =====================================================
# BUDGET DOCUMENTS VIEWS (Feature 4)
# =====================================================

@login_required
def budget_list(request):
    """
    Display list of Budget documents.
    """
    budgets = Budget.objects.all()
    
    # Filters
    b_type = request.GET.get('type')
    if b_type:
        budgets = budgets.filter(budget_type=b_type)
    
    fiscal_year = request.GET.get('year')
    if fiscal_year:
        budgets = budgets.filter(fiscal_year=fiscal_year)
    
    approved = request.GET.get('approved')
    if approved:
        budgets = budgets.filter(is_approved=(approved == 'true'))
    
    # Pagination
    paginator = Paginator(budgets, 20)
    page = request.GET.get('page')
    try:
        budgets = paginator.page(page)
    except PageNotAnInteger:
        budgets = paginator.page(1)
    except EmptyPage:
        budgets = paginator.page(paginator.num_pages)
    
    return render(request, 'documents/budget_list.html', {
        'budgets': budgets,
        'title': 'Budget Documents'
    })


@login_required
def budget_detail(request, slug):
    """
    Display Budget details.
    """
    budget = get_object_or_404(Budget, slug=slug)
    
    return render(request, 'documents/budget_detail.html', {
        'budget': budget,
        'title': budget.title
    })


# =====================================================
# MEMBER SPEECHES VIEWS (Feature 5)
# =====================================================

@login_required
def speech_list(request):
    """
    Display list of Member speeches in Parliament.
    """
    speeches = Speech.objects.all()
    
    # Filters
    s_type = request.GET.get('type')
    if s_type:
        speeches = speeches.filter(speech_type=s_type)
    
    member_id = request.GET.get('member')
    if member_id:
        speeches = speeches.filter(member_id=member_id)
    
    session = request.GET.get('session')
    if session:
        speeches = speeches.filter(session=session)
    
    # Search
    query = request.GET.get('q')
    if query:
        speeches = speeches.filter(
            models.Q(title__icontains=query) |
            models.Q(speech_text__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(speeches, 20)
    page = request.GET.get('page')
    try:
        speeches = paginator.page(page)
    except PageNotAnInteger:
        speeches = paginator.page(1)
    except EmptyPage:
        speeches = paginator.page(paginator.num_pages)
    
    return render(request, 'documents/speech_list.html', {
        'speeches': speeches,
        'title': 'Member Speeches'
    })


@login_required
def speech_detail(request, pk):
    """
    Display Speech details.
    """
    speech = get_object_or_404(Speech, pk=pk)
    
    return render(request, 'documents/speech_detail.html', {
        'speech': speech,
        'title': speech.title
    })


@login_required
def member_speeches(request, member_slug):
    """
    Display speeches by a specific member.
    """
    from members.models import Member
    member = get_object_or_404(Member, slug=member_slug)
    speeches = member.speeches.all()
    
    return render(request, 'documents/member_speeches.html', {
        'member': member,
        'speeches': speeches,
        'title': f"Speeches by {member.name}"
    })


# =====================================================
# ORDINANCE TRACKING VIEWS (Feature 6)
# =====================================================

@login_required
def ordinance_list(request):
    """
    Display list of Ordinances.
    """
    ordinances = Ordinance.objects.all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        ordinances = ordinances.filter(status=status)
    
    # Filter active only
    active_only = request.GET.get('active')
    if active_only == 'true':
        ordinances = ordinances.filter(status='issued')
    
    # Search
    query = request.GET.get('q')
    if query:
        ordinances = ordinances.filter(
            models.Q(title__icontains=query) |
            models.Q(ordinance_number__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(ordinances, 20)
    page = request.GET.get('page')
    try:
        ordinances = paginator.page(page)
    except PageNotAnInteger:
        ordinances = paginator.page(1)
    except EmptyPage:
        ordinances = paginator.page(paginator.num_pages)
    
    return render(request, 'documents/ordinance_list.html', {
        'ordinances': ordinances,
        'title': 'Ordinance Tracking'
    })


@login_required
def ordinance_detail(request, slug):
    """
    Display Ordinance details with status history.
    """
    ordinance = get_object_or_404(Ordinance, slug=slug)
    
    return render(request, 'documents/ordinance_detail.html', {
        'ordinance': ordinance,
        'title': f"Ordinance {ordinance.ordinance_number}"
    })


# =====================================================
# BOOKS VIEWS
# =====================================================

@login_required
def book_list(request):
    """
    Display list of books in the library.
    """
    books = Book.objects.select_related('document').all()
    
    # Filters
    genre = request.GET.get('genre')
    if genre:
        books = books.filter(genre=genre)
    
    author = request.GET.get('author')
    if author:
        books = books.filter(author__icontains=author)
    
    publisher = request.GET.get('publisher')
    if publisher:
        books = books.filter(publisher__icontains=publisher)
    
    year = request.GET.get('year')
    if year:
        books = books.filter(publication_year=year)
    
    available = request.GET.get('available')
    if available == 'true':
        books = books.filter(is_available=True)
    
    # Search
    query = request.GET.get('q')
    if query:
        books = books.filter(
            models.Q(document__title__icontains=query) |
            models.Q(author__icontains=query) |
            models.Q(isbn__icontains=query) |
            models.Q(document__keywords__icontains=query)
        )
    
    # Pagination
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except ValueError:
        per_page = 20
    
    paginator = Paginator(books, per_page)
    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    
    # Get genres for filter
    genres = Book.Genre.choices
    
    return render(request, 'documents/book_list.html', {
        'books': books,
        'genres': genres,
        'title': 'Library Books'
    })


@login_required
def book_detail(request, pk):
    """
    Display book details.
    """
    book = get_object_or_404(Book.objects.select_related('document'), pk=pk)
    
    # Track view
    if book.document:
        book.document.increment_view()
    
    # Get related books by same author or genre
    related_books = Book.objects.filter(
        models.Q(author=book.author) |
        models.Q(genre=book.genre)
    ).exclude(pk=book.pk).select_related('document')[:5]
    
    return render(request, 'documents/book_detail.html', {
        'book': book,
        'related_books': related_books,
        'title': book.title
    })
