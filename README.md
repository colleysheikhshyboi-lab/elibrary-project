# National Assembly of The Gambia - E-Library System

A secure, centralized digital repository for parliamentary documents, built with Django, HTML5, CSS3, and JavaScript.

## 📋 Overview

This e-Library system serves as a comprehensive document management solution for the National Assembly of The Gambia, providing:

- **Centralized Repository**: Single access point for Acts, Bills, Hansards, Committee Reports, and more
- **Role-Based Access Control**: Secure access for MPs, Clerks, Librarians, and Public users
- **Document Versioning**: Track changes and maintain audit trails
- **Powerful Search**: Full-text search across all document types
- **Secure Storage**: On-premise hosting with robust security measures

## 🏗️ Architecture

### Technology Stack

- **Backend**: Django 4.x (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla + Bootstrap 5)
- **Database**: PostgreSQL
- **Web Server**: Gunicorn + Nginx (Production)
- **Static Files**: WhiteNoise

### Project Structure

```
elibrary_project/
├── manage.py
├── requirements.txt
├── elibrary_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── apps.py
├── accounts/
│   ├── models.py (Custom User with roles)
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── documents/
│   ├── models.py (Document, Category, Versions)
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── context_processors.py
├── core/
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── accounts/
│   ├── documents/
│   └── core/
├── static/
│   ├── css/style.css
│   └── js/main.js
└── media/
    └── documents/
```

## 🚀 Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Git
- Virtual Environment (recommended)

### Setup Steps

1. **Clone and Setup**
```bash
cd /home/sheikh/Desktop
git clone <repository-url>
cd elibrary
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Database**
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE elibrary_db;
CREATE USER elibrary_admin WITH PASSWORD 'your_secure_password';
ALTER DATABASE elibrary_db OWNER TO elibrary_admin;
\q
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run Migrations**
```bash
python manage.py migrate
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Collect Static Files**
```bash
python manage.py collectstatic
```

8. **Run Development Server**
```bash
python manage.py runserver
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,.nationalassembly.gm

# Database Settings
DB_NAME=elibrary_db
DB_USER=elibrary_admin
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

### Production Deployment

#### Using Gunicorn

```bash
gunicorn elibrary_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Static files
    location /static/ {
        alias /path/to/elibrary/staticfiles/;
    }
    
    # Media files
    location /media/ {
        alias /path/to/elibrary/media/;
    }
    
    # Django app
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📚 User Roles

| Role | Permissions |
|------|-------------|
| **Administrator** | Full system access, user management, all documents |
| **Clerk/Staff** | Upload, edit, manage documents, view all |
| **Librarian/Research** | Upload, edit, manage documents, view all |
| **MP** | View and download all documents |
| **Public** | View public documents only |

## 📄 Document Types Supported

1. **Acts of Parliament** - Laws passed by the assembly
2. **Bills** - Proposed legislation
3. **Amendments** - Changes to bills/acts
4. **Hansards** - Official parliamentary records
5. **Committee Reports** - Findings from committees
6. **Parliamentary Journals** - Daily proceedings
7. **Gazettes** - Official publications
8. **Research Documents** - Research and analysis
9. **Contracts/Agreements** - Official documents
10. **Policy Documents** - Assembly policies

## 🔐 Security Features

- **HTTPS Encryption** - All communications encrypted
- **Role-Based Access Control** - Granular permissions
- **Session Management** - Secure 8-hour sessions
- **Password Policies** - Strong password requirements
- **Audit Logging** - Track all document access
- **File Validation** - Prevent malicious uploads
- **CSRF Protection** - Cross-site request forgery prevention
- **SQL Injection Prevention** - ORM-based data access

## 📊 Usage Statistics

The system tracks:
- Document views
- Document downloads
- User activity
- Access patterns

## 🛠️ Management Commands

```bash
# Create admin user
python manage.py createsuperuser

# Load sample data
python manage.py loaddata fixtures/sample_data.json

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Check system status
python manage.py check --deploy
```

## 📈 Maintenance

### Database Backup
```bash
pg_dump -U elibrary_admin elibrary_db > backup_$(date +%Y%m%d).sql
```

### Log Rotation
Configure logrotate for `/var/log/elibrary/elibrary.log`

### Regular Tasks
- Weekly database backups
- Monthly security updates
- Quarterly access reviews

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test documents

# Generate coverage report
coverage run --source='.' manage.py test
coverage report
```

## 📝 API Documentation

REST API endpoints are available at `/api/v1/`:

- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/{id}/` - Document details
- `POST /api/v1/documents/` - Create document (auth required)
- `GET /api/v1/search/` - Search documents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is proprietary software for the National Assembly of The Gambia.

## 🆘 Support

For technical support:
- Email: ict-support@parliament.gm
- Phone: +220 422 7621
- Location: National Assembly ICT Department

## 🙏 Acknowledgments

Built following best practices for:
- Django Software Foundation guidelines
- OWASP security recommendations
- WCAG 2.1 accessibility standards
- Parliamentary library management standards

---

**National Assembly of The Gambia - Modernizing Legislative Information Management**

