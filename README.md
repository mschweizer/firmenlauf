# Running Events Registration

A Django application for managing running event registrations. This application allows administrators to create running events and participants to register for these events.

## Features

- Create and manage running events with details like name, date, location, and description
- Set registration deadlines for events
- Limit the number of participants for events
- Register participants with details like name, department, year of birth, t-shirt size, and email
- Automatically place participants on a waiting list when an event is full
- Prevent duplicate registrations
- View registration details and status

## Installation

### Prerequisites

- Python 3.11 or higher
- Django 5.2 or higher

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/running-events-registration.git
   cd running-events-registration
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Usage

### Admin Interface

1. Access the admin interface at http://127.0.0.1:8000/admin/
2. Log in using the superuser credentials you created
3. Create running events with the following details:
   - Name
   - Date
   - Location
   - Description
   - Registration deadline (optional)
   - Maximum number of participants (optional)
4. View and manage participant registrations

### Public Interface

1. Visit the homepage at http://127.0.0.1:8000/
2. Browse available running events
3. Click on an event to view details and register
4. Fill out the registration form with your details
5. Submit the form to register for the event
6. If the event is full, you will be placed on a waiting list

## Development

### Settings Structure

This project uses a split settings structure:

- **base.py**: Common settings shared by all environments
- **development.py**: Development-specific settings (DEBUG=True, SQLite, etc.)
- **production.py**: Production-specific settings (DEBUG=False, PostgreSQL, security settings, etc.)

By default, the development settings are used when running the development server.

### Environment Variables

For production, you need to set environment variables. Copy the `.env.example` file to `.env` and update the values:

```bash
cp .env.example .env
# Edit .env with your actual values
```

Required environment variables for production:
- `DJANGO_SECRET_KEY`: A secret key for Django
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`: Database connection details
- `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email server details

### Code Quality Tools

This project uses several tools to maintain code quality:

- **pre-commit**: Runs checks before each commit
- **black**: Code formatter
- **isort**: Import sorter
- **flake8**: Linter
- **mypy**: Type checker

To set up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

### Running Tests

To run the tests:

```bash
python manage.py test
```

Or to run specific test files:

```bash
python manage.py test runs.tests.test_models
python manage.py test runs.tests.test_views
python manage.py test runs.tests.test_forms
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request
