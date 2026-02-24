"""
Data migration to add initial member data for testing.
"""

from django.db import migrations
from django.utils import timezone
from django.utils.text import slugify


def add_sample_members(apps, schema_editor):
    """Add sample parliamentary members."""
    Member = apps.get_model('members', 'Member')
    Party = apps.get_model('members', 'Party')
    Constituency = apps.get_model('members', 'Constituency')
    
    # Create sample parties
    udp, _ = Party.objects.get_or_create(
        abbreviation='UDP',
        defaults={
            'name': 'United Democratic Party',
            'color': '#ce1126',
            'founded_year': 1997,
            'ideology': 'Centrism, Liberalism',
            'is_active': True
        }
    )
    
    npp, _ = Party.objects.get_or_create(
        abbreviation='NPP',
        defaults={
            'name': 'National People\'s Party',
            'color': '#3c8d2f',
            'founded_year': 2019,
            'ideology': 'Populism',
            'is_active': True
        }
    )
    
    independent, _ = Party.objects.get_or_create(
        abbreviation='IND',
        defaults={
            'name': 'Independent',
            'color': '#6c757d',
            'is_active': True
        }
    )
    
    # Create sample constituencies
    banjul, _ = Constituency.objects.get_or_create(
        code='BAN',
        defaults={
            'name': 'Banjul',
            'region': 'Banjul',
            'population': 31343,
            'is_active': True
        }
    )
    
    kanifing, _ = Constituency.objects.get_or_create(
        code='KAN',
        defaults={
            'name': 'Kanifing',
            'region': 'Kanifing',
            'population': 382096,
            'is_active': True
        }
    )
    
    kuntaur, _ = Constituency.objects.get_or_create(
        code='KUN',
        defaults={
            'name': 'Kuntaur',
            'region': 'Central River',
            'population': 85097,
            'is_active': True
        }
    )
    
    # Create sample members
    members_data = [
        {
            'name': 'Hon. Fabakary S. Jatta',
            'constituency': 'Banjul',
            'constituency_code': 'BAN',
            'party': 'United Democratic Party',
            'party_abbreviation': 'UDP',
            'gender': 'male',
            'date_of_birth': '1960-05-15',
            'place_of_birth': 'Banjul',
            'first_elected': 2012,
            'parliament_number': 6,
            'is_speaker': True,
            'speaker': 'Speaker of the National Assembly',
            'committees': 'Committee on Privileges and Ethics, Committee on Rules and Procedures',
            'profession': 'Politician, Legal Professional',
            'education': 'LLB (Hons), Gambia Law School',
            'is_active': True,
            'sort_order': 1,
        },
        {
            'name': 'Hon. Fanta Bai Bagay',
            'constituency': 'Kanifing',
            'constituency_code': 'KAN',
            'party': 'National People\'s Party',
            'party_abbreviation': 'NPP',
            'gender': 'female',
            'date_of_birth': '1975-08-22',
            'place_of_birth': 'Serrekunda',
            'first_elected': 2021,
            'parliament_number': 6,
            'is_speaker': False,
            'committees': 'Women\'s Affairs Committee, Education Committee',
            'profession': 'Educationist',
            'education': 'BSc Education, University of Gambia',
            'is_active': True,
            'sort_order': 2,
        },
        {
            'name': 'Hon. Ousman S. Kandeh',
            'constituency': 'Kuntaur',
            'constituency_code': 'KUN',
            'party': 'United Democratic Party',
            'party_abbreviation': 'UDP',
            'gender': 'male',
            'date_of_birth': '1968-03-10',
            'place_of_birth': 'Kuntaur',
            'first_elected': 2017,
            'parliament_number': 6,
            'is_speaker': False,
            'committee_chair': 'Committee on Agriculture',
            'committees': 'Committee on Agriculture, Committee on Finance',
            'profession': 'Agricultural Extension Officer',
            'education': 'Diploma in Agriculture',
            'is_active': True,
            'sort_order': 3,
        },
        {
            'name': 'Hon. Dr. Demba A. Jallow',
            'constituency': 'Foni B. K. S',
            'constituency_code': 'FBK',
            'party': 'United Democratic Party',
            'party_abbreviation': 'UDP',
            'gender': 'male',
            'date_of_birth': '1972-11-25',
            'place_of_birth': 'Brikama',
            'first_elected': 2012,
            'parliament_number': 5,
            'is_speaker': False,
            'committee_chair': 'Committee on Health',
            'committees': 'Committee on Health, Committee on Social Affairs',
            'profession': 'Medical Doctor',
            'education': 'MBBS, University of Ghana',
            'is_active': True,
            'sort_order': 4,
        },
        {
            'name': 'Hon. Amie S. Joof',
            'constituency': 'Mansakonko',
            'constituency_code': 'MAN',
            'party': 'National People\'s Party',
            'party_abbreviation': 'NPP',
            'gender': 'female',
            'date_of_birth': '1980-07-14',
            'place_of_birth': 'Mansakonko',
            'first_elected': 2021,
            'parliament_number': 6,
            'is_speaker': True,
            'speaker': 'Deputy Speaker',
            'committees': 'Committee on Rules and Procedures',
            'profession': 'Politician',
            'education': 'BA Political Science',
            'is_active': True,
            'sort_order': 5,
        },
        {
            'name': 'Hon. Sulayman S. S. K. Samura',
            'constituency': 'Kerewan',
            'constituency_code': 'KER',
            'party': 'United Democratic Party',
            'party_abbreviation': 'UDP',
            'gender': 'male',
            'date_of_birth': '1965-02-28',
            'place_of_birth': 'Kerewan',
            'first_elected': 2007,
            'parliament_number': 5,
            'is_speaker': False,
            'committee_chair': 'Committee on Public Accounts',
            'committees': 'Committee on Public Accounts, Committee on Local Government',
            'profession': 'Civil Servant',
            'education': 'Advanced Certificate in Public Administration',
            'is_active': True,
            'sort_order': 6,
        },
    ]
    
    for data in members_data:
        # Generate slug from name
        data['slug'] = slugify(data['name'])
        Member.objects.get_or_create(
            name=data['name'],
            constituency=data['constituency'],
            defaults=data
        )


def remove_sample_members(apps, schema_editor):
    """Remove sample data (for rollback)."""
    Member = apps.get_model('members', 'Member')
    Party = apps.get_model('members', 'Party')
    Constituency = apps.get_model('members', 'Constituency')
    
    Member.objects.all().delete()
    Party.objects.all().delete()
    Constituency.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_sample_members, remove_sample_members),
    ]

