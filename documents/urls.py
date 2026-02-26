"""
URL patterns for documents app.
"""

from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document list and search
    path('', views.document_list, name='document_list'),
    path('search/', views.document_search, name='document_search'),
    path('stats/', views.document_stats, name='document_stats'),
    
    # Document upload
    path('upload/', views.document_upload, name='document_upload'),
    
    # Legislative Tracking (Bills) - must come before generic slug
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/<slug:slug>/', views.bill_detail, name='bill_detail'),
    
    # Parliamentary Questions
    path('questions/', views.question_list, name='question_list'),
    path('questions/<int:pk>/', views.question_detail, name='question_detail'),
    
    # Committees
    path('committees/', views.committee_list, name='committee_list'),
    path('committees/<slug:slug>/', views.committee_detail, name='committee_detail'),
    path('committees/<slug:committee_slug>/meetings/<int:meeting_id>/', 
         views.committee_meeting_detail, name='committee_meeting_detail'),
    
    # Budget Documents
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/<slug:slug>/', views.budget_detail, name='budget_detail'),
    
    # Member Speeches
    path('speeches/', views.speech_list, name='speech_list'),
    path('speeches/<int:pk>/', views.speech_detail, name='speech_detail'),
    path('members/<slug:member_slug>/speeches/', views.member_speeches, name='member_speeches'),
    
    # Ordinances
    path('ordinances/', views.ordinance_list, name='ordinance_list'),
    path('ordinances/<slug:slug>/', views.ordinance_detail, name='ordinance_detail'),
    
    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    
    # Document CRUD operations - must come last (generic slug pattern)
    path('<slug:slug>/', views.document_detail, name='document_detail'),
    path('<slug:slug>/download/', views.document_download, name='document_download'),
    path('<slug:slug>/edit/', views.document_edit, name='document_edit'),
    path('<slug:slug>/delete/', views.document_delete, name='document_delete'),
    path('<slug:slug>/publish/', views.document_publish, name='document_publish'),
    path('<slug:slug>/unpublish/', views.document_unpublish, name='document_unpublish'),
]
