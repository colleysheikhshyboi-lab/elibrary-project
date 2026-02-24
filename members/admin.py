"""
Admin configuration for the Members app.
"""

from django.contrib import admin
from .models import Member, Constituency, Party


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Admin configuration for Member model."""
    
    list_display = [
        'photo_preview', 'name', 'constituency', 'party', 
        'is_active', 'is_speaker', 'first_elected'
    ]
    list_filter = ['is_active', 'is_speaker', 'party', 'gender']
    search_fields = ['name', 'constituency', 'party', 'email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('photo', 'name', 'slug', 'gender', 'date_of_birth', 'place_of_birth')
        }),
        ('Parliamentary Information', {
            'fields': ('constituency', 'constituency_code', 'party', 'party_abbreviation')
        }),
        ('Positions', {
            'fields': ('is_speaker', 'speaker', 'committees', 'committee_chair')
        }),
        ('Term Information', {
            'fields': ('first_elected', 'term_start', 'term_end', 'parliament_number')
        }),
        ('Background', {
            'fields': ('education', 'profession')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'office_location')
        }),
        ('Social Media', {
            'fields': ('twitter', 'facebook', 'website'),
            'classes': ('collapse',)
        }),
        ('Additional Info', {
            'fields': ('biography', 'achievements', 'sort_order'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_retired')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def photo_preview(self, obj):
        """Display photo preview in admin list."""
        if obj.photo:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />',
                obj.photo.url
            )
        return '-'
    photo_preview.short_description = 'Photo'


@admin.register(Constituency)
class ConstituencyAdmin(admin.ModelAdmin):
    """Admin configuration for Constituency model."""
    
    list_display = ['name', 'code', 'region', 'population', 'member_count', 'is_active']
    list_filter = ['region', 'is_active']
    search_fields = ['name', 'code', 'region']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    """Admin configuration for Party model."""
    
    list_display = ['abbreviation', 'name', 'founded_year', 'ideology', 'member_count', 'is_active']
    list_filter = ['is_active', 'founded_year']
    search_fields = ['name', 'abbreviation']
    readonly_fields = ['created_at', 'updated_at']

