"""
API Serializers for the e-Library system.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from members.models import Member, Constituency, Party
from documents.models import Document, DocumentCategory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class MemberListSerializer(serializers.ModelSerializer):
    """Serializer for Member list view."""
    
    party_abbreviation = serializers.CharField(source='party_abbreviation', read_only=True)
    
    class Meta:
        model = Member
        fields = ['id', 'name', 'slug', 'photo', 'gender', 'constituency', 
                  'party', 'party_abbreviation', 'is_speaker', 'is_active',
                  'get_absolute_url']


class MemberDetailSerializer(serializers.ModelSerializer):
    """Serializer for Member detail view."""
    
    committees_list = serializers.SerializerMethodField()
    chairs_list = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True)
    term_duration = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Member
        fields = [
            'id', 'name', 'slug', 'photo', 'gender', 'date_of_birth',
            'place_of_birth', 'constituency', 'constituency_code', 'party',
            'party_abbreviation', 'is_speaker', 'speaker', 'committees',
            'committees_list', 'committee_chair', 'chairs_list',
            'first_elected', 'term_start', 'term_end', 'parliament_number',
            'education', 'profession', 'email', 'phone', 'office_location',
            'twitter', 'facebook', 'website', 'biography', 'achievements',
            'is_active', 'is_retired', 'age', 'term_duration'
        ]
    
    def get_committees_list(self, obj):
        return obj.get_committees_list
    
    def get_chairs_list(self, obj):
        return obj.get_chairs_list


class ConstituencySerializer(serializers.ModelSerializer):
    """Serializer for Constituency model."""
    
    member_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Constituency
        fields = ['id', 'name', 'code', 'region', 'population', 
                  'area_sq_km', 'voters_count', 'capital', 'map_coordinates',
                  'is_active', 'member_count']


class PartySerializer(serializers.ModelSerializer):
    """Serializer for Party model."""
    
    member_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Party
        fields = ['id', 'name', 'abbreviation', 'logo', 'color', 
                  'founded_year', 'ideology', 'website', 'is_active',
                  'member_count']


class DocumentCategorySerializer(serializers.ModelSerializer):
    """Serializer for DocumentCategory model."""
    
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'is_active']


class DocumentListSerializer(serializers.ModelSerializer):
    """Serializer for Document list view."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'slug', 'document_type', 'category', 'category_name',
            'file', 'thumbnail', 'description', 'keywords', 'access_level',
            'uploaded_by', 'uploaded_by_name', 'created_at', 'updated_at',
            'published_at', 'is_published', 'view_count', 'download_count',
            'get_absolute_url'
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Serializer for Document detail view."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    versions = serializers.SerializerMethodField()
    related_documents = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'slug', 'document_type', 'category', 'category_name',
            'file', 'thumbnail', 'description', 'keywords', 'access_level',
            'act_number', 'bill_number', 'year', 'volume', 'pages',
            'uploaded_by', 'uploaded_by_name', 'created_at', 'updated_at',
            'published_at', 'is_published', 'is_featured', 'view_count',
            'download_count', 'versions', 'related_documents', 'get_absolute_url'
        ]
    
    def get_versions(self, obj):
        from documents.models import DocumentVersion
        versions = obj.versions.all()[:5]
        return DocumentVersionSerializer(versions, many=True).data
    
    def get_related_documents(self, obj):
        from documents.models import Document
        related = Document.objects.filter(
            document_type=obj.document_type,
            is_published=True
        ).exclude(id=obj.id)[:5]
        return DocumentListSerializer(related, many=True).data


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Serializer for DocumentVersion model."""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        from documents.models import DocumentVersion
        model = DocumentVersion
        fields = ['id', 'version', 'file', 'changes', 'uploaded_by',
                  'uploaded_by_name', 'created_at']

