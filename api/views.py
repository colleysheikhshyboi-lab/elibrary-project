"""
API Views for the e-Library system.
"""

from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Sum
from django.contrib.auth import get_user_model

from members.models import Member, Constituency, Party
from documents.models import Document, DocumentCategory
from .serializers import (
    UserSerializer,
    MemberListSerializer, MemberDetailSerializer,
    ConstituencySerializer, PartySerializer,
    DocumentCategorySerializer,
    DocumentListSerializer, DocumentDetailSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for User model.
    Lists users and retrieves user details.
    """
    
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']


class MemberViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for Member model.
    Provides list, retrieve, and stats endpoints.
    """
    
    queryset = Member.objects.filter(is_active=True)
    serializer_class = MemberListSerializer
    permission_classes = [permissions.AllowAny]  # Publicly accessible
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'constituency', 'party', 'profession']
    ordering_fields = ['name', 'constituency', 'party', 'first_elected']
    ordering = ['name']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MemberDetailSerializer
        return MemberListSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get member statistics."""
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
        
        return Response({
            'total': members.count(),
            'party_breakdown': list(party_stats),
            'gender_breakdown': gender_stats,
            'constituencies': constituency_count,
            'speakers': members.filter(is_speaker=True).count(),
        })
    
    @action(detail=False, methods=['get'])
    def parties(self, request):
        """Get list of parties with member counts."""
        parties = Party.objects.filter(is_active=True).annotate(
            member_count=Count('member')
        ).order_by('name')
        return Response(PartySerializer(parties, many=True).data)
    
    @action(detail=False, methods=['get'])
    def constituencies(self, request):
        """Get list of constituencies with member counts."""
        constituencies = Constituency.objects.filter(is_active=True).annotate(
            member_count=Count('member')
        ).order_by('name')
        return Response(ConstituencySerializer(constituencies, many=True).data)


class ConstituencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for Constituency model.
    """
    
    queryset = Constituency.objects.filter(is_active=True)
    serializer_class = ConstituencySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'region']
    ordering_fields = ['name', 'code', 'region']
    ordering = ['name']


class PartyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for Party model.
    """
    
    queryset = Party.objects.filter(is_active=True)
    serializer_class = PartySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'abbreviation']
    ordering_fields = ['name', 'abbreviation']
    ordering = ['name']


class DocumentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for DocumentCategory model.
    """
    
    queryset = DocumentCategory.objects.filter(is_active=True)
    serializer_class = DocumentCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    ordering = ['name']


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for Document model.
    Requires authentication for access.
    """
    
    queryset = Document.objects.filter(is_published=True)
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'keywords', 'act_number', 'bill_number']
    ordering_fields = ['title', 'created_at', 'published_at', 'view_count', 'download_count']
    ordering = ['-published_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by document type
        doc_type = self.request.query_params.get('type')
        if doc_type:
            queryset = queryset.filter(document_type=doc_type)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        # Filter by access level
        access_level = self.request.query_params.get('access')
        if access_level:
            queryset = queryset.filter(access_level=access_level)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get document types with counts."""
        from documents.models import Document
        types = []
        for doc_type in Document.DocumentType.choices:
            count = Document.objects.filter(
                document_type=doc_type[0],
                is_published=True
            ).count()
            types.append({
                'value': doc_type[0],
                'label': doc_type[1],
                'count': count
            })
        return Response(types)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get document statistics."""
        from documents.models import Document
        
        stats = {
            'total_documents': Document.objects.filter(is_published=True).count(),
            'total_views': Document.objects.aggregate(
                total=models.Sum('view_count')
            )['total'] or 0,
            'total_downloads': Document.objects.aggregate(
                total=models.Sum('download_count')
            )['total'] or 0,
            'by_type': {},
            'by_year': {},
        }
        
        # Count by type
        for doc_type in Document.DocumentType.choices:
            count = Document.objects.filter(
                document_type=doc_type[0],
                is_published=True
            ).count()
            stats['by_type'][doc_type[1]] = count
        
        # Count by year
        years = Document.objects.filter(
            is_published=True
        ).values_list('year', flat=True).distinct().order_by('-year')
        for year in years:
            if year:
                count = Document.objects.filter(year=year, is_published=True).count()
                stats['by_year'][year] = count
        
        return Response(stats)

