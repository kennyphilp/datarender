# School Rolls Data Application

A Django-based web application for visualizing and analyzing historical school enrollment data from 1996 to 2018. The application provides interactive data tables, filtering capabilities, and enrollment trend visualizations.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Security](#security)
- [Accessibility](#accessibility)
- [Browser Support](#browser-support)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Data Exploration
- **Interactive Data Table**: View school enrollment data with sorting capabilities
- **Advanced Filtering**: Filter by school name, sector, and school type
- **Pagination**: Efficient data loading with configurable page sizes (default: 200 schools per page)
- **Persistent Selections**: Automatically saves filter selections to browser localStorage

### Visualizations
- **Enrollment Trends Graph**: Interactive line charts showing enrollment trends over time
- **Multi-School Comparison**: Compare up to 50 schools simultaneously
- **Export Functionality**: Download graphs as PNG images
- **Dark Theme**: Modern dark-themed visualizations matching the application design

### User Experience
- **Responsive Design**: Mobile-first design that works on all device sizes
- **Accessibility**: WCAG 2.1 compliant with ARIA labels and keyboard navigation
- **Error Handling**: User-friendly error messages with automatic retry functionality
- **Loading States**: Clear feedback during data loading operations

### Technical Features
- **Type Safety**: Full Python type hints for better IDE support and code quality
- **Comprehensive Testing**: 21 automated tests covering models, API, graphs, and integrations
- **Logging**: Structured logging for debugging and monitoring
- **API Versioning**: RESTful API with versioning support (v1)
- **Security**: Environment-based configuration, SQL injection prevention

## 🛠 Technology Stack

### Backend
- **Django 6.0**: Web framework
- **Python 3.12**: Programming language
- **SQLite**: Database (two databases: default + datastore)
- **Matplotlib**: Graph generation with Agg backend

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **CSS3**: Modern responsive design with CSS variables
- **HTML5**: Semantic markup with accessibility features

### Development Tools
- **Git**: Version control
- **Virtual Environment**: Python dependency isolation

## 📦 Prerequisites

- Python 3.12 or higher
- pip (Python package installer)
- Git
- 500MB free disk space

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd proj1
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3.12 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Expected packages:
- Django==6.0
- matplotlib
- Other dependencies as listed in requirements.txt

### 4. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

Required environment variables:
- `DJANGO_SECRET_KEY`: Secret key for Django (generate a secure random string)
- `DJANGO_DEBUG`: Set to 'False' for production

### 5. Initialize Database

```bash
cd myproject

# Run migrations for default database
python manage.py migrate

# Note: datastore.db should already contain the school rolls data
# If not, run the import script:
python ../scripts/load_csv_to_db.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Secret key for Django (generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DJANGO_SECRET_KEY=your-secret-key-here

# Debug mode (True for development, False for production)
DJANGO_DEBUG=True
```

### Application Constants

Configuration values can be adjusted in `home/constants.py`:

```python
# Pagination settings
DEFAULT_PAGE_SIZE = 200  # Default number of schools per page
MAX_PAGE_SIZE = 1000     # Maximum allowed page size

# Graph settings
MAX_SCHOOLS_PER_GRAPH = 50  # Maximum schools in a single graph
GRAPH_COLOR_PALETTE = ['#6366f1', '#f59e0b', ...]  # Graph colors

# Data range
DATA_START_YEAR = 1996
DATA_END_YEAR = 2018
```

### Logging Configuration

Logs are written to `logs/` directory:
- `logs/django.log`: Django framework logs (WARNING level and above)
- `logs/app.log`: Application logs (INFO level and above)

Log rotation: 10MB per file, 5 backup files retained.

## 🏃 Running the Application

### Development Server

```bash
cd myproject

# Start the development server
python manage.py runserver

# Or use the convenience script
./scripts/start_app.zsh
```

The application will be available at: http://127.0.0.1:8000

### Stopping the Server

```bash
# Ctrl+C in the terminal, or
./scripts/stop_app.zsh
```

### Accessing the Application

- **Home Page**: http://127.0.0.1:8000/
- **Data Explorer**: http://127.0.0.1:8000/data/
- **API Endpoint**: http://127.0.0.1:8000/api/v1/data/
- **Graph API**: http://127.0.0.1:8000/api/v1/enrollment-graph/

## 🧪 Running Tests

### Run All Tests

```bash
cd myproject
python manage.py test home
```

### Run Specific Test Class

```bash
python manage.py test home.tests.DataAPITests
python manage.py test home.tests.EnrollmentGraphTests
```

### Run with Verbose Output

```bash
python manage.py test home --verbosity=2
```

### Test Coverage

The test suite includes 21 tests covering:
- **Model Tests** (2): SchoolRoll model serialization
- **API Tests** (10): Pagination, filtering, sorting, validation, security
- **Graph Tests** (6): Graph generation, parameter handling, limits
- **Integration Tests** (3): Page rendering, UI elements
- **Constants Tests** (3): Configuration validation

See `TESTING.md` for detailed test documentation.

## 📁 Project Structure

```
proj1/
├── myproject/                  # Django project root
│   ├── myproject/             # Project settings
│   │   ├── settings.py        # Django configuration
│   │   ├── urls.py            # URL routing
│   │   └── wsgi.py            # WSGI application
│   ├── home/                  # Main application
│   │   ├── models.py          # SchoolRoll model
│   │   ├── views.py           # API and page views
│   │   ├── urls.py            # URL patterns
│   │   ├── constants.py       # Application constants
│   │   └── tests.py           # Test suite
│   ├── templates/             # HTML templates
│   │   └── home/
│   │       ├── index.html     # Home page
│   │       └── data.html      # Data explorer
│   ├── static/                # Static files
│   │   ├── css/
│   │   │   ├── style.css      # Global styles
│   │   │   └── data-page.css  # Data page styles
│   │   └── js/
│   │       └── data-page.js   # Data page JavaScript
│   ├── logs/                  # Application logs
│   ├── db.sqlite3             # Default Django database
│   ├── datastore.db           # School rolls data
│   └── manage.py              # Django management script
├── scripts/                   # Utility scripts
│   ├── load_csv_to_db.py      # CSV import script
│   ├── start_app.zsh          # Start server script
│   └── stop_app.zsh           # Stop server script
├── .venv/                     # Virtual environment
├── .env                       # Environment variables (not in git)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore patterns
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── TESTING.md                 # Test documentation
```

## 📡 API Documentation

### API Versioning

The API uses versioning with the `/api/v1/` prefix. Legacy endpoints without version prefix are maintained for backward compatibility.

### Data API

**Endpoint**: `GET /api/v1/data/`

Returns paginated school roll data with filtering and sorting capabilities.

**Query Parameters**:
- `page` (int, optional): Page number (1-based, default: 1)
- `page_size` (int, optional): Items per page (default: 200, max: 1000)
- `sort` (string, optional): Column name to sort by (default: 'Name')
- `order` (string, optional): Sort order 'asc' or 'desc' (default: 'asc')
- `sector` (string, optional): Filter by sector
- `schools` (array, optional): Filter by school names (can be repeated)

**Response**:
```json
{
  "page": 1,
  "page_size": 200,
  "total": 3150,
  "total_pages": 16,
  "columns": ["Name", "Sector", "School_Type", "1996", ...],
  "data": [
    {
      "ObjectId": "abc123",
      "Name": "Example School",
      "Sector": "Secondary",
      "School_Type": "Academy",
      "F1996": 850,
      "F1997": 875,
      ...
    }
  ],
  "distinct": {
    "names": [{"id": "abc123", "name": "Example School"}, ...],
    "sectors": ["Primary", "Secondary", ...],
    "types": ["Academy", "Community", ...]
  }
}
```

**Example**:
```bash
curl "http://127.0.0.1:8000/api/v1/data/?page=1&page_size=50&sector=Secondary&order=desc"
```

### Enrollment Graph API

**Endpoint**: `GET /api/v1/enrollment-graph/`

Generates a PNG image showing enrollment trends for selected schools.

**Query Parameters**:
- `ids` (array, required): ObjectId values of schools (can be repeated, max: 50)
- `schools` (array, optional): School names as fallback (can be repeated)

**Response**: PNG image (image/png)

**Example**:
```bash
curl "http://127.0.0.1:8000/api/v1/enrollment-graph/?ids=abc123&ids=def456" -o graph.png
```

**Graph Features**:
- Dark theme matching application design
- Up to 6 distinct colors for clarity
- Automatic limiting to 50 schools maximum
- Null value handling (data gaps)
- Legend with school names

## 💻 Development

### Code Style

The project follows PEP 8 style guidelines for Python code:
- 4 spaces for indentation
- Type hints for all function signatures
- Docstrings for all public functions and classes
- Line length limit: 100 characters

### Type Hints

All Python code uses type hints for better IDE support:

```python
from typing import Dict, List, Optional
from django.http import HttpRequest, JsonResponse

def data_api(request: HttpRequest) -> JsonResponse:
    """API endpoint with type hints."""
    pass
```

### Adding New Features

1. Create a feature branch
2. Implement changes with tests
3. Run test suite: `python manage.py test home`
4. Update documentation
5. Submit pull request

### Database Schema

The `school_rolls` table contains:
- **ObjectId** (VARCHAR, PRIMARY KEY): Unique school identifier
- **Code** (VARCHAR): School code
- **Name** (VARCHAR): School name (indexed)
- **LA_Code** (VARCHAR): Local Authority code
- **LA_Name** (VARCHAR): Local Authority name
- **Sector** (VARCHAR): Education sector (indexed)
- **School_Type** (VARCHAR): Type of school (indexed)
- **F1996-F2018** (INTEGER): Enrollment counts for each year

## 🔒 Security

### Best Practices Implemented

1. **Environment Variables**: Sensitive data stored in `.env` file
2. **SQL Injection Prevention**: Parameterized queries and ORM usage
3. **Input Validation**: All user inputs validated and sanitized
4. **CSRF Protection**: Django CSRF middleware enabled
5. **Secure Headers**: XSS protection, clickjacking prevention
6. **Secret Key**: Stored securely in environment variables

### Security Checklist for Production

- [ ] Set `DJANGO_DEBUG=False` in production
- [ ] Use a strong, random `DJANGO_SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` in settings.py
- [ ] Use HTTPS (configure SSL/TLS)
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Review security headers
- [ ] Run `python manage.py check --deploy`

## ♿ Accessibility

### WCAG 2.1 Compliance

The application implements accessibility best practices:

- **ARIA Labels**: All interactive elements properly labeled
- **Keyboard Navigation**: Full keyboard support (Tab, Enter, Space)
- **Screen Reader Support**: Semantic HTML and ARIA live regions
- **Color Contrast**: Sufficient contrast ratios for text and UI elements
- **Focus Indicators**: Visible focus states for all interactive elements
- **Alternative Text**: Descriptive alt text for graphs and images

### Keyboard Shortcuts

- **Tab**: Navigate between interactive elements
- **Enter/Space**: Activate buttons and checkboxes
- **Arrow Keys**: Navigate within select boxes
- **Escape**: Close modals and dialogs

## 🌐 Browser Support

### Supported Browsers

- **Chrome/Edge**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Mobile Safari**: iOS 12+
- **Chrome Mobile**: Latest version

### Required Features

- ES6 JavaScript (async/await, arrow functions, template literals)
- CSS Grid and Flexbox
- Fetch API
- localStorage
- CSS Variables

## 🐛 Troubleshooting

### Common Issues

#### Port 8000 Already in Use

```bash
# Find the process
lsof -i :8000

# Kill the process
kill <PID>

# Or use the stop script
./scripts/stop_app.zsh
```

#### Database Locked Error

```bash
# Close all connections to the database
# Restart the Django server
python manage.py runserver
```

#### Missing datastore.db

```bash
# Run the CSV import script
cd proj1
python scripts/load_csv_to_db.py
```

#### Static Files Not Loading

```bash
# Collect static files (production)
python manage.py collectstatic

# Check STATICFILES_DIRS in settings.py
```

#### Log Files Growing Too Large

Log files automatically rotate at 10MB. To manually clear:

```bash
rm logs/*.log
```

### Debug Mode

Enable verbose logging by setting in `.env`:

```env
DJANGO_DEBUG=True
```

Then check logs in:
- Console output
- `logs/django.log`
- `logs/app.log`

## 🤝 Contributing

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Pull Request Guidelines

- Include tests for new features
- Update documentation
- Follow existing code style
- Ensure all tests pass
- Add entry to CHANGELOG.md

### Reporting Issues

When reporting issues, please include:
- Browser and version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Error messages from logs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- School enrollment data sourced from [Data Source]
- Built with Django and Python
- Visualization powered by Matplotlib
- Dark theme inspired by modern design principles

## 📞 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Email: [support email]
- Documentation: [docs URL]

## 🗺 Roadmap

### Planned Features

- [ ] Export data to CSV/Excel
- [ ] Advanced search with fuzzy matching
- [ ] User authentication and saved views
- [ ] Dashboard with summary statistics
- [ ] Comparison mode for multiple time periods
- [ ] Data import from additional sources
- [ ] REST API documentation (Swagger/OpenAPI)
- [ ] Docker containerization
- [ ] CI/CD pipeline

### Version History

- **v1.0.0** (Current)
  - Initial release
  - Data exploration and filtering
  - Enrollment trend visualizations
  - Responsive design
  - Accessibility features
  - Comprehensive test suite

---

**Last Updated**: December 2025  
**Maintained By**: [Your Team/Name]  
**Version**: 1.0.0
