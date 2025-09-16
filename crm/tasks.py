import os
import logging
from datetime import datetime
from celery import shared_task
from django.db import transaction
from crm.models import Customer, Order
from django.db.models import Sum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report with total customers, orders, and revenue.
    Logs the report to /tmp/crm_report_log.txt with timestamp.
    """
    try:
        # Use Django ORM to fetch data (equivalent to GraphQL queries)
        with transaction.atomic():
            # Total number of customers
            total_customers = Customer.objects.count()
            
            # Total number of orders
            total_orders = Order.objects.count()
            
            # Total revenue (sum of totalamount from orders)
            total_revenue = Order.objects.aggregate(
                total=Sum('totalamount')
            )['total'] or 0
            
        # Format the report
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, {total_revenue} revenue"
        )
        
        # Log to file
        log_file_path = '/tmp/crm_report_log.txt'
        
        # Ensure directory exists (for Windows compatibility)
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        try:
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(report_message + '\n')
        except (IOError, OSError) as e:
            # Fallback to alternative log location if /tmp is not accessible
            fallback_path = 'crm_report_log.txt'
            try:
                with open(fallback_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(report_message + '\n')
                logger.warning(f"Could not write to {log_file_path}, used fallback {fallback_path}")
            except (IOError, OSError) as fallback_error:
                logger.error(f"Failed to write to both {log_file_path} and {fallback_path}: {fallback_error}")
                raise
        
        # Also log to Django logger
        logger.info(f"CRM Report generated: {report_message}")
        
        return {
            'status': 'success',
            'message': report_message,
            'customers': total_customers,
            'orders': total_orders,
            'revenue': float(total_revenue)
        }
        
    except Exception as e:
        error_message = f"Error generating CRM report: {str(e)}"
        logger.error(error_message)
        
        # Log error to file as well
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_log = f"{timestamp} - ERROR: {error_message}"
        
        try:
            with open('/tmp/crm_report_log.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(error_log + '\n')
        except (IOError, OSError):
            try:
                with open('crm_report_log.txt', 'a', encoding='utf-8') as log_file:
                    log_file.write(error_log + '\n')
            except (IOError, OSError):
                pass  # If we can't log to file, at least we logged to Django logger
        
        return {
            'status': 'error',
            'message': error_message
        }

@shared_task
def test_celery_connection():
    """
    Simple test task to verify Celery is working.
    """
    return "Celery is working correctly!"