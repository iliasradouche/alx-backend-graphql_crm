#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        filename='/tmp/order_reminders_log.txt',
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def get_graphql_client():
    """Initialize GraphQL client"""
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        headers={'Content-Type': 'application/json'}
    )
    return Client(transport=transport, fetch_schema_from_transport=True)

def get_pending_orders_query():
    """GraphQL query to get orders from the last 7 days"""
    return gql("""
        query GetRecentOrders {
            allOrders {
                id
                orderNumber
                totalAmount
                status
                createdAt
                customer {
                    id
                    email
                    firstName
                    lastName
                }
            }
        }
    """)

def filter_recent_orders(orders):
    """Filter orders from the last 7 days"""
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_orders = []
    
    for order in orders:
        # Parse the created_at timestamp
        try:
            order_date = datetime.fromisoformat(order['createdAt'].replace('Z', '+00:00'))
            if order_date.replace(tzinfo=None) >= seven_days_ago:
                recent_orders.append(order)
        except (ValueError, KeyError) as e:
            continue
    
    return recent_orders

def send_order_reminders():
    """Main function to process order reminders"""
    logger = setup_logging()
    
    try:
        # Initialize GraphQL client
        client = get_graphql_client()
        
        # Execute query
        query = get_pending_orders_query()
        result = client.execute(query)
        
        # Get all orders
        all_orders = result.get('allOrders', [])
        
        # Filter orders from the last 7 days
        recent_orders = filter_recent_orders(all_orders)
        
        # Log each order
        for order in recent_orders:
            customer = order.get('customer', {})
            customer_email = customer.get('email', 'No email')
            order_id = order.get('id')
            order_number = order.get('orderNumber', 'N/A')
            status = order.get('status', 'N/A')
            
            log_message = f"Order ID: {order_id}, Order Number: {order_number}, Status: {status}, Customer Email: {customer_email}"
            logger.info(log_message)
        
        # Log summary
        summary_message = f"Processed {len(recent_orders)} orders from the last 7 days"
        logger.info(summary_message)
        
        # Print to console
        print("Order reminders processed!")
        
    except Exception as e:
        error_message = f"Error processing order reminders: {str(e)}"
        logger.error(error_message)
        print(f"Error: {error_message}")
        sys.exit(1)

if __name__ == '__main__':
    send_order_reminders()