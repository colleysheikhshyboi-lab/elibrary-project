from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds role-based access control for parliamentary library system.
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        CLERK = 'clerk', 'Clerk/Staff'
        LIBRARIAN = 'librarian', 'Library/Research Officer'
        MP = 'mp', 'Member of Parliament'
        PUBLIC = 'public', 'Public User'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PUBLIC,
        verbose_name='User Role'
    )
    
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Employee ID'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Department'
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Phone Number'
    )
    
    library_card_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Library Card Number'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date of Birth'
    )
    
    # Permissions flags
    can_upload = models.BooleanField(
        default=False,
        verbose_name='Can Upload Documents'
    )
    can_delete = models.BooleanField(
        default=False,
        verbose_name='Can Delete Documents'
    )
    can_manage_users = models.BooleanField(
        default=False,
        verbose_name='Can Manage Users'
    )
    can_view_all_documents = models.BooleanField(
        default=False,
        verbose_name='Can View All Documents'
    )
    
    # Tracking
    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Last Login IP'
    )
    password_changed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Password Last Changed'
    )
    account_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Account Expiration Date'
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        permissions = [
            ('view_audit_log', 'Can view audit logs'),
            ('export_documents', 'Can export documents'),
            ('bulk_upload', 'Can bulk upload documents'),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
    
    @property
    def is_mp(self):
        return self.role == self.Role.MP
    
    @property
    def is_librarian(self):
        return self.role in [self.Role.LIBRARIAN, self.Role.CLERK]
    
    @property
    def can_access_restricted(self):
        """Check if user can access restricted documents."""
        return self.role in [
            self.Role.ADMIN,
            self.Role.CLERK,
            self.Role.LIBRARIAN,
            self.Role.MP
        ]
    
    def save(self, *args, **kwargs):
        # Set staff status based on role
        if self.role in [self.Role.ADMIN, self.Role.CLERK, self.Role.LIBRARIAN]:
            self.is_staff = True
        
        # Set permissions based on role
        if self.role == self.Role.ADMIN:
            self.can_upload = True
            self.can_delete = True
            self.can_manage_users = True
            self.can_view_all_documents = True
        elif self.role in [self.Role.CLERK, self.Role.LIBRARIAN]:
            self.can_upload = True
            self.can_delete = False
            self.can_manage_users = False
            self.can_view_all_documents = True
        elif self.role == self.Role.MP:
            self.can_upload = False
            self.can_delete = False
            self.can_manage_users = False
            self.can_view_all_documents = True
        
        super().save(*args, **kwargs)
