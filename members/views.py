"""
Views for the Parliamentary Members directory.
"""

from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Member, Constituency, Party


def member_list(request):
    """
    Display a directory of parliamentary members with filtering and search.
    This view is publicly accessible.
    """
    members = Member.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        members = members.filter(
            Q(name__icontains=search_query) |
            Q(constituency__icontains=search_query) |
            Q(party__icontains=search_query) |
            Q(profession__icontains=search_query)
        )
    
    # Filter by party
    party_filter = request.GET.get('party')
    if party_filter:
        members = members.filter(party__icontains=party_filter)
    
    # Filter by constituency
    constituency_filter = request.GET.get('constituency')
    if constituency_filter:
        members = members.filter(constituency__icontains=constituency_filter)
    
    # Filter by gender
    gender_filter = request.GET.get('gender')
    if gender_filter:
        members = members.filter(gender=gender_filter)
    
    # Filter by status (speaker/deputy)
    speaker_filter = request.GET.get('speaker')
    if speaker_filter == 'yes':
        members = members.filter(is_speaker=True)
    
    # Sorting
    sort = request.GET.get('sort', 'name')
    sort_options = {
        'name': 'name',
        'constituency': 'constituency',
        'party': 'party',
        'recent': '-first_elected',
    }
    sort_key = sort_options.get(sort, 'name')
    members = members.order_by(sort_key)
    
    # Pagination
    paginator = Paginator(members, 20)
    page = request.GET.get('page')
    try:
        members_page = paginator.page(page)
    except PageNotAnInteger:
        members_page = paginator.page(1)
    except EmptyPage:
        members_page = paginator.page(paginator.num_pages)
    
    # Get filter options for sidebar
    parties = Member.objects.filter(
        is_active=True, 
        party__isnull=False
    ).exclude(party='').values_list('party', flat=True).distinct().order_by('party')
    
    constituencies = Member.objects.filter(
        is_active=True
    ).values_list('constituency', flat=True).distinct().order_by('constituency')
    
    # Get statistics
    stats = {
        'total': Member.objects.filter(is_active=True).count(),
        'male': Member.objects.filter(is_active=True, gender='male').count(),
        'female': Member.objects.filter(is_active=True, gender='female').count(),
        'speakers': Member.objects.filter(is_active=True, is_speaker=True).count(),
        'parties': len(set(parties)),
    }
    
    return render(request, 'members/member_list.html', {
        'members': members_page,
        'parties': parties,
        'constituencies': constituencies,
        'stats': stats,
        'title': 'Members Directory - National Assembly',
        'search_query': search_query or '',
    })


def member_detail(request, slug):
    """
    Display detailed information about a specific member.
    This view is publicly accessible.
    """
    member = get_object_or_404(Member, slug=slug, is_active=True)
    
    # Get related members from same constituency or party
    same_constituency = Member.objects.filter(
        constituency__icontains=member.constituency,
        is_active=True
    ).exclude(id=member.id)[:4]
    
    same_party = Member.objects.filter(
        party__icontains=member.party,
        is_active=True
    ).exclude(id=member.id)[:4]
    
    # Get other speakers
    other_speakers = Member.objects.filter(
        is_speaker=True,
        is_active=True
    ).exclude(id=member.id)[:4]
    
    return render(request, 'members/member_detail.html', {
        'member': member,
        'same_constituency': same_constituency,
        'same_party': same_party,
        'other_speakers': other_speakers,
        'title': f'{member.name} - Member Profile',
    })


def member_stats(request):
    """
    Display statistics about parliamentary members.
    """
    members = Member.objects.filter(is_active=True)
    
    # Party breakdown
    party_stats = members.values('party').annotate(
        count=Count('id')
    ).filter(party__isnull=False).exclude(party='').order_by('-count')
    
    # Gender breakdown
    gender_stats = {
        'male': members.filter(gender='male').count(),
        'female': members.filter(gender='female').count(),
        'other': members.filter(gender='other').count(),
    }
    
    # Constituency count
    constituency_count = members.values('constituency').distinct().count()
    
    # Term information
    avg_years = 0
    terms = [m.term_duration for m in members if m.term_duration]
    if terms:
        avg_years = sum(terms) / len(terms)
    
    stats = {
        'total': members.count(),
        'party_breakdown': list(party_stats),
        'gender_breakdown': gender_stats,
        'constituencies': constituency_count,
        'average_term_years': round(avg_years, 1),
    }
    
    return render(request, 'members/member_stats.html', {
        'stats': stats,
        'title': 'Members Statistics - National Assembly',
    })


def constituency_list(request):
    """
    Display a list of constituencies with member counts.
    """
    constituencies = Constituency.objects.filter(is_active=True).order_by('name')
    
    return render(request, 'members/constituency_list.html', {
        'constituencies': constituencies,
        'title': 'Constituencies - National Assembly',
    })


def party_list(request):
    """
    Display a list of political parties with member counts.
    """
    parties = Party.objects.filter(is_active=True).order_by('name')
    
    return render(request, 'members/party_list.html', {
        'parties': parties,
        'title': 'Political Parties - National Assembly',
    })

