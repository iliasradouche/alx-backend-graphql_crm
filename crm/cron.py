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

if __name__ == '__main__':
    # Allow running the function directly for testing
    log_crm_heartbeat()