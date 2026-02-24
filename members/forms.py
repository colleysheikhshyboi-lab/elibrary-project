"""
Forms for the Members app.
"""

from django import forms
from .models import Member


class MemberSearchForm(forms.Form):
    """Form for searching members."""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, constituency, party...'
        })
    )
    
    party = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    constituency = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    gender = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All'),
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('name', 'Name (A-Z)'),
            ('constituency', 'Constituency'),
            ('party', 'Party'),
            ('recent', 'Most Recent First'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class MemberAdminForm(forms.ModelForm):
    """Admin form for Member model."""
    
    class Meta:
        model = Member
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'constituency': forms.TextInput(attrs={'class': 'form-control'}),
            'party': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'committees': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

