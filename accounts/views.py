"""
Views for user authentication and management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_protect
from .models import User
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    CustomAuthenticationForm,
    UserProfileForm,
    PasswordChangeForm
)


@csrf_protect
def login_view(request):
    """
    User login view with security features.
    """
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Update last login info
            user.last_login = timezone.now()
            user.last_login_ip = get_client_ip(request)
            user.save(update_fields=['last_login', 'last_login_ip'])
            
            # Handle remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            
            # Redirect to next page or dashboard
            next_page = request.GET.get('next', '/dashboard/')
            return redirect(next_page)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'title': 'Login'
    })


def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """
    User dashboard showing relevant information based on role.
    """
    user = request.user
    
    if user.role == User.Role.ADMIN:
        return render(request, 'accounts/dashboard_admin.html', {
            'title': 'Admin Dashboard'
        })
    elif user.role == User.Role.CLERK:
        return render(request, 'accounts/dashboard_clerk.html', {
            'title': 'Clerk Dashboard'
        })
    elif user.role == User.Role.LIBRARIAN:
        return render(request, 'accounts/dashboard_librarian.html', {
            'title': 'Librarian Dashboard'
        })
    elif user.role == User.Role.MP:
        return render(request, 'accounts/dashboard_mp.html', {
            'title': 'MP Dashboard'
        })
    else:
        return render(request, 'accounts/dashboard_public.html', {
            'title': 'Dashboard'
        })


@login_required
def profile_view(request):
    """
    View and edit user profile.
    """
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'title': 'My Profile'
    })


@login_required
def change_password_view(request):
    """
    Change user password.
    """
    user = request.user
    
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                update_session_auth_hash(request, user)
                
                # Update password change timestamp
                user.password_changed_at = timezone.now()
                user.save(update_fields=['password_changed_at'])
            
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('profile')
    else:
        form = PasswordChangeForm(user)
    
    return render(request, 'accounts/change_password.html', {
        'form': form,
        'title': 'Change Password'
    })


@login_required
@permission_required('accounts.view_user', raise_exception=True)
def user_list_view(request):
    """
    List all users (admin/HR only).
    """
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role if specified
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Filter by active status
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
    
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'title': 'User Management'
    })


@login_required
@permission_required('accounts.add_user', raise_exception=True)
def user_create_view(request):
    """
    Create a new user.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data.get('password1') or None)
                user.save()
                
                messages.success(request, f'User {user.get_full_name()} has been created successfully.')
                return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Create User'
    })


@login_required
@permission_required('accounts.change_user', raise_exception=True)
def user_update_view(request, user_id):
    """
    Update an existing user.
    """
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.get_full_name()} has been updated successfully.')
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': f'Edit User: {user.get_full_name()}'
    })


@login_required
@permission_required('accounts.delete_user', raise_exception=True)
def user_delete_view(request, user_id):
    """
    Delete a user (soft delete by deactivating).
    """
    user = get_object_or_404(User, pk=user_id)
    
    if request.user == user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_list')
    
    if request.method == 'POST':
        with transaction.atomic():
            # Soft delete - just deactivate
            user.is_active = False
            user.save()
            
            messages.success(request, f'User {user.get_full_name()} has been deactivated.')
            return redirect('user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {
        'user': user,
        'title': 'Deactivate User'
    })


@login_required
@permission_required('accounts.change_user', raise_exception=True)
def user_toggle_active_view(request, user_id):
    """
    Toggle user active status.
    """
    user = get_object_or_404(User, pk=user_id)
    
    if request.user == user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('user_list')
    
    with transaction.atomic():
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.get_full_name()} has been {status}.')
    
    return redirect('user_list')


def get_client_ip(request):
    """
    Get client IP address from request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
