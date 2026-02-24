"""
URL patterns for the Members app.
"""

from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    # Main member directory
    path('', views.member_list, name='member_list'),
    
    # Statistics page (must come before slug pattern)
    path('stats/', views.member_stats, name='member_stats'),
    
    # Constituency list (must come before slug pattern)
    path('constituencies/', views.constituency_list, name='constituency_list'),
    
    # Party list (must come before slug pattern)
    path('parties/', views.party_list, name='party_list'),
    
    # Member detail page (must come last as it's the most generic)
    path('<slug:slug>/', views.member_detail, name='member_detail'),
]

