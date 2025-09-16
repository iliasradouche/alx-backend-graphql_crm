# CRM Celery Task Configuration

This document provides setup instructions for the Celery task system that generates weekly CRM reports using Celery Beat scheduling.

## Overview

The CRM system includes a Celery task that:
- Generates weekly reports with total customers, orders, and revenue
- Runs every Monday at 6:00 AM UTC
- Logs reports to `/tmp/crm_report_log.txt`
- Uses Redis as the message broker
- Integrates with the existing GraphQL schema and Django models

## Prerequisites

- Python 3.8+
- Django 4.2+
- Redis server
- All dependencies from `requirements.txt`

## Installation and Setup

### 1. Install Redis

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### On macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

#### On Windows:
- Download Redis from: https://github.com/microsoftarchive/redis/releases
- Or use Docker: `docker run -d -p 6379:6379 redis:alpine`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

The following Celery-related packages are included:
- `celery>=5.3.0`
- `django-celery-beat>=2.5.0`
- `redis>=4.5.0`

### 3. Run Database Migrations

```bash
python manage.py migrate
```

This creates the necessary tables for django-celery-beat to store periodic task information.

### 4. Verify Redis Connection

Test that Redis is running:
```bash
redis-cli ping
```
Expected response: `PONG`

## Running the Celery System

### 1. Start Celery Worker

In one terminal, start the Celery worker:
```bash
celery -A crm worker -l info
```

### 2. Start Celery Beat Scheduler

In another terminal, start the Celery Beat scheduler:
```bash
celery -A crm beat -l info
```

### 3. Optional: Start Celery Flower (Monitoring)

For task monitoring (optional):
```bash
pip install flower
celery -A crm flower
```
Then visit: http://localhost:5555

## Task Configuration

### Weekly Report Task

The `generate_crm_report` task is configured to run:
- **Schedule**: Every Monday at 6:00 AM UTC
- **Task**: `crm.tasks.generate_crm_report`
- **Output**: Logs to `/tmp/crm_report_log.txt`

### Manual Task Execution

To manually trigger the report generation:

```python
# In Django shell (python manage.py shell)
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.get())
```

### Test Celery Connection

```python
# In Django shell
from crm.tasks import test_celery_connection
result = test_celery_connection.delay()
print(result.get())  # Should print: "Celery is working correctly!"
```

## Verification

### 1. Check Log Files

Verify that reports are being generated:
```bash
# On Unix/Linux/macOS
tail -f /tmp/crm_report_log.txt

# On Windows (if /tmp is not accessible, check project root)
type crm_report_log.txt
```

### 2. Expected Log Format

```
2024-01-15 06:00:01 - Report: 150 customers, 75 orders, 12500.50 revenue
2024-01-22 06:00:01 - Report: 155 customers, 82 orders, 13200.75 revenue
```

### 3. Check Celery Beat Schedule

Verify the scheduled task is registered:
```bash
celery -A crm inspect scheduled
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis is running: `redis-cli ping`
   - Check Redis URL in settings: `redis://localhost:6379/0`

2. **Permission Error on Log File**
   - The task automatically falls back to `crm_report_log.txt` in the project root
   - Ensure write permissions for the chosen directory

3. **Task Not Executing**
   - Verify both Celery worker and beat are running
   - Check Django migrations are applied
   - Ensure `django_celery_beat` is in `INSTALLED_APPS`

4. **Import Errors**
   - Ensure all dependencies are installed
   - Check that `crm.celery` app is properly imported in `__init__.py`

### Debug Commands

```bash
# List all registered tasks
celery -A crm inspect registered

# Check active tasks
celery -A crm inspect active

# Check scheduled tasks
celery -A crm inspect scheduled

# Purge all tasks
celery -A crm purge
```

## Configuration Files

- **Celery App**: `crm/celery.py`
- **Tasks**: `crm/tasks.py`
- **Settings**: `crm/settings.py` (Celery configuration)
- **Dependencies**: `requirements.txt`

## Production Considerations

1. **Security**: Change Redis configuration for production use
2. **Monitoring**: Use Flower or other monitoring tools
3. **Logging**: Configure proper log rotation for report files
4. **Scaling**: Consider multiple workers for high-volume tasks
5. **Persistence**: Use Redis persistence or alternative result backends

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Celery logs for error messages
3. Verify Redis connectivity and Django database access
4. Ensure all migrations are applied and dependencies installed