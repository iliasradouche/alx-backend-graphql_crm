#!/bin/bash

# Script to clean inactive customers with no orders since a year ago
# This script uses Django's manage.py shell to execute Python commands

# Set the Django project directory (adjust path as needed)
PROJECT_DIR="/path/to/your/django/project"
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Change to project directory
cd "$PROJECT_DIR"

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Execute Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from datetime import datetime, timedelta
from django.utils import timezone
from crm.models import Customer, Order

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since one year ago
inactive_customers = Customer.objects.exclude(
    id__in=Order.objects.filter(
        created_at__gte=one_year_ago
    ).values_list('customer_id', flat=True)
)

# Count and delete inactive customers
deleted_count = inactive_customers.count()
inactive_customers.delete()

print(deleted_count)
")

# Log the result with timestamp
echo "[$TIMESTAMP] Cleaned up $DELETED_COUNT inactive customers" >> "$LOG_FILE"

# Exit with success status
exit 0