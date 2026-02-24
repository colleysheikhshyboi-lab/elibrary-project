"""
Models for the Parliamentary Members directory.
"""

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class MemberManager(models.Manager):
    """Custom manager for Member model."""
    
    def active(self):
        """Return only active members."""
        return self.filter(is_active=True)
    
    def by_party(self, party):
        """Filter members by party."""
        return self.filter(party=party)
    
    def by_constituency(self, constituency):
        """Filter members by constituency."""
        return self.filter(constituency__icontains=constituency)
    
    def speakers(self):
        """Return members who are speakers/deputy speakers."""
        return self.filter(speaker__isnull=False)


class Member(models.Model):
    """
    Model representing a Member of Parliament.
    Stores detailed information about parliamentary members.
    """
    
    class Meta:
        verbose_name = 'Member of Parliament'
        verbose_name_plural = 'Members of Parliament'
        ordering = ['name']
        permissions = [
            ('view_member_details', 'Can view member details'),
            ('export_member_data', 'Can export member data'),
        ]
    
    # Personal Information
    name = models.CharField(
        max_length=200,
        verbose_name='Full Name'
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name='URL Slug'
    )
    photo = models.ImageField(
        upload_to='members/photos/',
        null=True,
        blank=True,
        verbose_name='Profile Photo'
    )
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        verbose_name='Gender'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date of Birth'
    )
    place_of_birth = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Place of Birth'
    )
    
    # Parliamentary Information
    constituency = models.CharField(
        max_length=200,
        verbose_name='Constituency'
    )
    constituency_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name='Constituency Code'
    )
    party = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Political Party'
    )
    party_abbreviation = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name='Party Abbreviation'
    )
    
    # Parliamentary Roles
    speaker = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Speaker/Position'
    )
    is_speaker = models.BooleanField(
        default=False,
        verbose_name='Is Speaker/Deputy Speaker'
    )
    
    # Committee Memberships
    committees = models.TextField(
        null=True,
        blank=True,
        verbose_name='Committee Memberships',
        help_text='List of committees the member belongs to'
    )
    committee_chair = models.TextField(
        null=True,
        blank=True,
        verbose_name='Committee Chair Positions'
    )
    
    # Parliamentary Service
    first_elected = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1960), MaxValueValidator(2100)],
        verbose_name='First Elected Year'
    )
    term_start = models.DateField(
        null=True,
        blank=True,
        verbose_name='Current Term Start'
    )
    term_end = models.DateField(
        null=True,
        blank=True,
        verbose_name='Current Term End'
    )
    parliament_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name='Parliament Number'
    )
    
    # Educational Background
    education = models.TextField(
        null=True,
        blank=True,
        verbose_name='Educational Background'
    )
    profession = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Profession/Occupation'
    )
    
    # Contact Information
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='Email Address'
    )
    phone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Phone Number'
    )
    office_location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Office Location'
    )
    
    # Social Media (optional)
    twitter = models.URLField(
        null=True,
        blank=True,
        verbose_name='Twitter Profile'
    )
    facebook = models.URLField(
        null=True,
        blank=True,
        verbose_name='Facebook Profile'
    )
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name='Personal Website'
    )
    
    # Additional Information
    biography = models.TextField(
        null=True,
        blank=True,
        verbose_name='Biography'
    )
    achievements = models.TextField(
        null=True,
        blank=True,
        verbose_name='Notable Achievements'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Member'
    )
    is_retired = models.BooleanField(
        default=False,
        verbose_name='Retired Member'
    )
    
    # Ordering
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Sort Order'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Manager
    objects = MemberManager()
    
    def __str__(self):
        return f"{self.name} ({self.constituency})"
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def get_committees_list(self):
        """Return committees as a list."""
        if not self.committees:
            return []
        return [c.strip() for c in self.committees.split(',')]
    
    @property
    def get_chairs_list(self):
        """Return committee chairs as a list."""
        if not self.committee_chair:
            return []
        return [c.strip() for c in self.committee_chair.split(',')]
    
    @property
    def age(self):
        """Calculate current age."""
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def term_duration(self):
        """Calculate term duration in years."""
        if not self.term_start:
            return None
        from datetime import date
        today = date.today()
        if self.term_end:
            end_date = self.term_end
        else:
            end_date = today
        return end_date.year - self.term_start.year
    
    def get_absolute_url(self):
        """Get the absolute URL for this member."""
        from django.urls import reverse
        return reverse('members:member_detail', kwargs={'slug': self.slug})


class Constituency(models.Model):
    """
    Model representing parliamentary constituencies.
    Used for organizing members and providing constituency information.
    """
    
    class Meta:
        verbose_name = 'Constituency'
        verbose_name_plural = 'Constituencies'
        ordering = ['name']
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Constituency Name'
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Constituency Code'
    )
    region = models.CharField(
        max_length=100,
        verbose_name='Region'
    )
    population = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Population'
    )
    area_sq_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Area (sq km)'
    )
    voters_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Registered Voters'
    )
    
    # Geographic info
    capital = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Capital/Town'
    )
    map_coordinates = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Map Coordinates'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Constituency'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def member_count(self):
        """Get count of active members for this constituency."""
        return Member.objects.filter(
            constituency__icontains=self.name,
            is_active=True
        ).count()


class Party(models.Model):
    """
    Model representing political parties.
    Used for organizing members by party affiliation.
    """
    
    class Meta:
        verbose_name = 'Political Party'
        verbose_name_plural = 'Political Parties'
        ordering = ['name']
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Party Name'
    )
    abbreviation = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Abbreviation'
    )
    logo = models.ImageField(
        upload_to='parties/logos/',
        null=True,
        blank=True,
        verbose_name='Party Logo'
    )
    color = models.CharField(
        max_length=7,
        default='#000000',
        verbose_name='Party Color',
        help_text='Hex color code for party branding'
    )
    founded_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2100)],
        verbose_name='Founded Year'
    )
    ideology = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Political Ideology'
    )
    
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name='Party Website'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Party'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.abbreviation} - {self.name}"
    
    @property
    def member_count(self):
        """Get count of active members of this party."""
        return Member.objects.filter(
            party=self.name,
            is_active=True
        ).count()

