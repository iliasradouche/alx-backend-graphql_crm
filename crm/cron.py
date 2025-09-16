import os
import django
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportError

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

def log_crm_heartbeat():
    """
    Log a heartbeat message to confirm CRM application health.
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    Optionally queries GraphQL hello field to verify endpoint responsiveness.
    """
    # Get current timestamp in the required format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # Base heartbeat message
    heartbeat_message = f"{timestamp} CRM is alive"
    
    # Optional GraphQL health check
    graphql_status = ""
    try:
        # Initialize GraphQL client
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            headers={'Content-Type': 'application/json'},
            timeout=5  # 5 second timeout
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # Simple query to test GraphQL endpoint
        query = gql("""
            query {
                __schema {
                    queryType {
                        name
                    }
                }
            }
        """)
        
        # Execute query
        result = client.execute(query)
        if result and '__schema' in result:
            graphql_status = " - GraphQL endpoint responsive"
        else:
            graphql_status = " - GraphQL endpoint returned unexpected response"
            
    except TransportError as e:
        graphql_status = f" - GraphQL endpoint unreachable: {str(e)}"
    except Exception as e:
        graphql_status = f" - GraphQL health check failed: {str(e)}"
    
    # Complete message with GraphQL status
    complete_message = heartbeat_message + graphql_status
    
    # Append to log file
    log_file_path = '/tmp/crm_heartbeat_log.txt'
    try:
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(complete_message + '\n')
    except Exception as e:
        # Fallback: try to write to a local file if /tmp is not accessible (Windows)
        try:
            fallback_path = 'crm_heartbeat_log.txt'
            with open(fallback_path, 'a', encoding='utf-8') as log_file:
                log_file.write(complete_message + '\n')
        except Exception as fallback_error:
            # If all else fails, print to console
            print(f"Failed to write heartbeat log: {str(e)}, {str(fallback_error)}")
            print(complete_message)

def update_low_stock():
    """
    Execute UpdateLowStockProducts GraphQL mutation to update products with stock < 10.
    Logs updated product names and new stock levels with timestamp.
    """
    # Get current timestamp
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    try:
        # Initialize GraphQL client
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            headers={'Content-Type': 'application/json'},
            timeout=30  # 30 second timeout for mutation
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # Define the UpdateLowStockProducts mutation
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    message
                    count
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)
        
        # Execute the mutation
        result = client.execute(mutation)
        
        if result and 'updateLowStockProducts' in result:
            mutation_result = result['updateLowStockProducts']
            
            if mutation_result['success']:
                log_message = f"{timestamp} Low stock update successful: {mutation_result['message']}"
                
                # Log details of updated products
                if mutation_result['updatedProducts']:
                    for product in mutation_result['updatedProducts']:
                        product_log = f"{timestamp} Updated product: {product['name']} - New stock: {product['stock']}"
                        log_message += f"\n{product_log}"
                else:
                    log_message += f"\n{timestamp} No products required stock updates"
            else:
                log_message = f"{timestamp} Low stock update failed: {mutation_result.get('message', 'Unknown error')}"
        else:
            log_message = f"{timestamp} Low stock update failed: Invalid response from GraphQL endpoint"
            
    except TransportError as e:
        log_message = f"{timestamp} Low stock update failed: GraphQL endpoint unreachable - {str(e)}"
    except Exception as e:
        log_message = f"{timestamp} Low stock update failed: {str(e)}"
    
    # Write to log file
    log_file_path = '/tmp/low_stock_updates_log.txt'
    try:
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_message + '\n')
    except Exception as e:
        # Fallback: try to write to a local file if /tmp is not accessible (Windows)
        try:
            fallback_path = 'low_stock_updates_log.txt'
            with open(fallback_path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_message + '\n')
        except Exception as fallback_error:
            # If all else fails, print to console
            print(f"Failed to write low stock update log: {str(e)}, {str(fallback_error)}")
            print(log_message)


if __name__ == '__main__':
    # Allow running the functions directly for testing
    log_crm_heartbeat()
    update_low_stock()