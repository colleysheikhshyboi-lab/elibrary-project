"""
Tests for the documents application.
"""

import pytest
from documents.models import Document, DocumentCategory, DocumentAccessLog


class TestDocumentCategory:
    """Tests for the DocumentCategory model."""

    def test_category_creation(self, document_category):
        """Test creating a document category."""
        assert document_category.name == 'Acts of Parliament'
        assert document_category.slug == 'acts-of-parliament'
        assert document_category.is_active

    def test_category_str_representation(self, document_category):
        """Test category string representation."""
        assert str(document_category) == 'Acts of Parliament'

    def test_category_ordering(self, db):
        """Test category ordering."""
        cat1 = DocumentCategory.objects.create(
            name='Category B',
            slug='category-b',
            order=2
        )
        cat2 = DocumentCategory.objects.create(
            name='Category A',
            slug='category-a',
            order=1
        )
        categories = list(DocumentCategory.objects.all())
        assert categories[0].name == 'Category A'
        assert categories[1].name == 'Category B'

    def test_category_unique_slug(self, db):
        """Test category slug is unique."""
        cat1 = DocumentCategory.objects.create(
            name='Test Category',
            slug='unique-slug'
        )
        assert cat1.slug == 'unique-slug'


class TestDocumentModel:
    """Tests for the Document model."""

    def test_document_creation(self, sample_document):
        """Test creating a document."""
        assert sample_document.title == 'Test Act of Parliament'
        assert sample_document.document_type == Document.DocumentType.ACT
        assert sample_document.is_published
        assert sample_document.access_level == Document.AccessLevel.PUBLIC

    def test_document_str_representation(self, sample_document):
        """Test document string representation."""
        str_repr = str(sample_document)
        assert 'Test Act of Parliament' in str_repr
        assert 'Act' in str_repr

    def test_document_slug_generation(self, db, admin_user, document_category):
        """Test automatic slug generation."""
        doc = Document.objects.create(
            title='New Test Document',
            document_type=Document.DocumentType.BILL,
            category=document_category,
            uploaded_by=admin_user
        )
        assert doc.slug == 'new-test-document'

    def test_document_unique_slug(self, db, admin_user, document_category):
        """Test unique slug generation for duplicate titles."""
        doc1 = Document.objects.create(
            title='Same Title',
            document_type=Document.DocumentType.BILL,
            category=document_category,
            uploaded_by=admin_user
        )
        doc2 = Document.objects.create(
            title='Same Title',
            document_type=Document.DocumentType.BILL,
            category=document_category,
            uploaded_by=admin_user
        )
        assert doc1.slug == 'same-title'
        assert doc2.slug == 'same-title-1'

    def test_document_is_restricted_public(self, sample_document):
        """Test is_restricted returns False for public documents."""
        assert not sample_document.is_restricted

    def test_document_is_restricted_confidential(self, restricted_document):
        """Test is_restricted returns True for confidential documents."""
        assert restricted_document.is_restricted

    def test_document_file_extension(self, sample_document):
        """Test getting file extension."""
        sample_document.file.name = 'documents/test/file.pdf'
        assert sample_document.get_file_extension() == '.pdf'

    def test_document_file_size_mb(self, sample_document):
        """Test getting file size in MB."""
        sample_document.file_size = 1048576  # 1 MB
        assert sample_document.get_file_size_mb() == 1.0

    def test_document_increment_download(self, sample_document):
        """Test incrementing download counter."""
        initial_count = sample_document.download_count
        sample_document.increment_download()
        assert sample_document.download_count == initial_count + 1

    def test_document_increment_view(self, sample_document):
        """Test incrementing view counter."""
        initial_count = sample_document.view_count
        sample_document.increment_view()
        assert sample_document.view_count == initial_count + 1

    def test_document_published_at_set(self, db, admin_user, document_category):
        """Test published_at is set when document is published."""
        doc = Document.objects.create(
            title='Test Document',
            document_type=Document.DocumentType.ACT,
            category=document_category,
            is_published=True,
            uploaded_by=admin_user
        )
        assert doc.published_at is not None

    def test_document_versioning(self, sample_document):
        """Test document version field."""
        assert sample_document.version == '1.0'


class TestDocumentAccessLog:
    """Tests for document access logging."""

    def test_access_log_creation(self, sample_document, admin_user):
        """Test creating an access log entry."""
        log = DocumentAccessLog.objects.create(
            document=sample_document,
            user=admin_user,
            action=DocumentAccessLog.Action.VIEW,
            ip_address='127.0.0.1'
        )
        assert log.document == sample_document
        assert log.user == admin_user
        assert log.action == DocumentAccessLog.Action.VIEW

    def test_access_log_actions(self, sample_document, admin_user):
        """Test access log action choices."""
        assert DocumentAccessLog.Action.VIEW == 'view'
        assert DocumentAccessLog.Action.DOWNLOAD == 'download'
        assert DocumentAccessLog.Action.PRINT == 'print'
        assert DocumentAccessLog.Action.SHARE == 'share'


class TestDocumentChoices:
    """Tests for document choice fields."""

    def test_document_type_choices(self, sample_document):
        """Test document type choices."""
        types = Document.DocumentType.choices
        assert ('act', 'Act of Parliament') in types
        assert ('bill', 'Bill') in types
        assert ('hansard', 'Hansard') in types
        assert ('committee_report', 'Committee Report') in types
        assert ('research', 'Research Document') in types

    def test_access_level_choices(self, sample_document):
        """Test access level choices."""
        levels = Document.AccessLevel.choices
        assert ('public', 'Public') in levels
        assert ('restricted', 'Restricted') in levels
        assert ('confidential', 'Confidential') in levels
        assert ('classified', 'Classified') in levels

    def test_document_url_patterns_configured(self, client):
        """Test document URLs are configured."""
        response = client.get('/documents/')
        # Should return 200 or redirect
        assert response.status_code in [200, 302]


class TestDocumentForms:
    """Tests for document forms."""

    def test_document_form_fields(self, db, admin_user, document_category):
        """Test document form has expected fields."""
        from documents.forms import DocumentForm
        form = DocumentForm()
        assert 'title' in form.fields
        assert 'document_type' in form.fields
        assert 'description' in form.fields
        assert 'access_level' in form.fields

    def test_search_form_fields(self, db):
        """Test search form has expected fields."""
        from search.forms import AdvancedSearchForm
        form = AdvancedSearchForm()
        assert 'q' in form.fields
        assert 'document_type' in form.fields
        assert 'year' in form.fields


class TestDocumentPermissions:
    """Tests for document permissions."""

    def test_admin_can_upload(self, admin_user):
        """Test admin user can upload documents."""
        assert admin_user.can_upload

    def test_clerk_can_upload(self, clerk_user):
        """Test clerk user can upload documents."""
        assert clerk_user.can_upload

    def test_mp_cannot_upload(self, mp_user):
        """Test MP user cannot upload documents."""
        assert not mp_user.can_upload

    def test_public_cannot_upload(self, public_user):
        """Test public user cannot upload documents."""
        assert not public_user.can_upload

    def test_admin_can_delete(self, admin_user):
        """Test admin user can delete documents."""
        assert admin_user.can_delete

    def test_clerk_cannot_delete(self, clerk_user):
        """Test clerk user cannot delete documents."""
        assert not clerk_user.can_delete

    def test_admin_can_manage_users(self, admin_user):
        """Test admin user can manage users."""
        assert admin_user.can_manage_users

    def test_clerk_cannot_manage_users(self, clerk_user):
        """Test clerk user cannot manage users."""
        assert not clerk_user.can_manage_users

