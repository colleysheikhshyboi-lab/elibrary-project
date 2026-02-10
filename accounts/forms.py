"""
Forms for user authentication and management.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form with additional fields.
    Used for new user registration by admins.
    """
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'role', 'employee_id', 'department', 
            'phone_number', 'library_card_number'
        )
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Employee ID'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'library_card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Library Card Number'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password fields optional for admin creation
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        for fieldname in ['password1', 'password2']:
            self.fields[fieldname].help_text = None
    
    def clean_password2(self):
        # Allow admin to create users without setting password immediately
        return self.cleaned_data.get('password2')


class CustomUserChangeForm(UserChangeForm):
    """
    Custom user change form for editing user profiles.
    """
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'role', 'employee_id', 'department', 
            'phone_number', 'library_card_number',
            'date_of_birth', 'is_active', 'can_upload',
            'can_delete', 'can_manage_users', 'can_view_all_documents'
        )
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'library_card_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form with enhanced security.
    """
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Employee ID',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Remember me for 8 hours'
    )
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.request = request
        self.user_cache = None


class UserProfileForm(forms.ModelForm):
    """
    Form for users to update their own profile.
    """
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'phone_number', 'department'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department'
            }),
        }


class PasswordChangeForm(forms.Form):
    """
    Custom password change form.
    """
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current Password'
        }),
        required=True
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        }),
        required=True
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        }),
        required=True
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                'Your old password was entered incorrectly. Please enter it again.'
            )
        return old_password
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    "The two password fields don't match."
                )
        
        # Validate password strength
        if len(password2) < 12:
            raise forms.ValidationError(
                "Password must be at least 12 characters long."
            )
        
        return password2
    
    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
