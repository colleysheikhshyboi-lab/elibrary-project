"""
Pytest configuration and fixtures for e-library tests.
"""

import pytest
from django.contrib.auth import get_user_model
from documents.models import Document, DocumentCategory

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    user = User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='TestPass123!',
        first_name='Admin',
        last_name='User',
        role=User.Role.ADMIN,
        employee_id='EMP001'
    )
    return user


@pytest.fixture
def clerk_user(db):
    """Create a clerk user for testing."""
    user = User.objects.create_user(
        username='clerk',
        email='clerk@test.com',
        password='TestPass123!',
        first_name='Clerk',
        last_name='User',
        role=User.Role.CLERK,
        employee_id='EMP002'
    )
    return user


@pytest.fixture
def mp_user(db):
    """Create an MP user for testing."""
    user = User.objects.create_user(
        username='mp',
        email='mp@test.com',
        password='TestPass123!',
        first_name='Member',
        last_name='Parliament',
        role=User.Role.MP,
        employee_id='EMP003'
    )
    return user


@pytest.fixture
def public_user(db):
    """Create a public user for testing."""
    user = User.objects.create_user(
        username='public',
        email='public@test.com',
        password='TestPass123!',
        first_name='Public',
        last_name='User',
        role=User.Role.PUBLIC
    )
    return user


@pytest.fixture
def authenticated_client(client, admin_user):
    """Return a logged-in client."""
    client.login(username='admin', password='TestPass123!')
    return client


@pytest.fixture
def document_category(db):
    """Create a document category for testing."""
    category = DocumentCategory.objects.create(
        name='Acts of Parliament',
        slug='acts-of-parliament',
        description='Official acts passed by the National Assembly',
        icon='file-text',
        color='#007bff',
        order=1,
        is_active=True
    )
    return category


@pytest.fixture
def sample_document(db, admin_user, document_category):
    """Create a sample document for testing."""
    document = Document.objects.create(
        title='Test Act of Parliament',
        slug='test-act-parliament',
        document_type=Document.DocumentType.ACT,
        category=document_category,
        description='A test document for unit testing',
        keywords='test, parliament, act',
        access_level=Document.AccessLevel.PUBLIC,
        is_published=True,
        uploaded_by=admin_user,
        year=2024,
        version='1.0',
        session='First Session'
    )
    return document


@pytest.fixture
def restricted_document(db, admin_user, document_category):
    """Create a restricted document for testing."""
    document = Document.objects.create(
        title='Confidential Report',
        slug='confidential-report',
        document_type=Document.DocumentType.RESEARCH_DOCUMENT,
        category=document_category,
        description='A confidential document',
        access_level=Document.AccessLevel.CONFIDENTIAL,
        is_published=True,
        uploaded_by=admin_user,
        year=2024
    )
    return document

