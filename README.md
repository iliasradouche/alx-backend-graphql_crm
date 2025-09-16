# ALX Backend GraphQL CRM

A Django-based Customer Relationship Management (CRM) system with GraphQL API and automated task scheduling.

## Features

- **GraphQL API**: Query and mutate customer and order data using GraphQL
- **Customer Management**: Track customer information and activity
- **Order Management**: Manage customer orders and status
- **Automated Cleanup**: Scheduled task to remove inactive customers
- **Admin Interface**: Django admin for easy data management

## Project Structure

```
alx-backend-graphql_crm/
├── crm/
│   ├── cron_jobs/
│   │   ├── clean_inactive_customers.sh
│   │   └── customer_cleanup_crontab.txt
│   ├── models.py
│   ├── schema.py
│   ├── admin.py
│   ├── views.py
│   └── urls.py
├── crm_project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
├── manage.py
└── requirements.txt
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```

## GraphQL Endpoint

Access the GraphQL interface at: `http://localhost:8000/graphql/`

### Sample Queries

**Get All Customers**:
```graphql
query {
  allCustomers {
    id
    firstName
    lastName
    email
    isActive
  }
}
```

**Create Customer**:
```graphql
mutation {
  createCustomer(
    firstName: "John"
    lastName: "Doe"
    email: "john.doe@example.com"
    phone: "+1234567890"
  ) {
    customer {
      id
      fullName
      email
    }
  }
}
```

## Cron Job Setup

The project includes automated cleanup of inactive customers:

1. **Shell Script**: `crm/cron_jobs/clean_inactive_customers.sh`
   - Deletes customers with no orders in the past year
   - Logs cleanup results to `/tmp/customer_cleanup_log.txt`

2. **Crontab Entry**: `crm/cron_jobs/customer_cleanup_crontab.txt`
   - Runs every Sunday at 2:00 AM
   - Format: `0 2 * * 0`

### Installing the Cron Job

```bash
# Make script executable (Linux/Mac)
chmod +x crm/cron_jobs/clean_inactive_customers.sh

# Add to crontab
crontab crm/cron_jobs/customer_cleanup_crontab.txt
```

## Models

### Customer
- `first_name`, `last_name`: Customer name
- `email`: Unique email address
- `phone`: Contact number
- `address`: Customer address
- `is_active`: Active status
- `created_at`, `updated_at`: Timestamps

### Order
- `customer`: Foreign key to Customer
- `order_number`: Unique order identifier
- `total_amount`: Order total
- `status`: Order status (pending, completed, cancelled)
- `notes`: Additional order notes
- `created_at`, `updated_at`: Timestamps

## Admin Interface

Access the Django admin at: `http://localhost:8000/admin/`

## Development

This project is part of the ALX Backend Development curriculum focusing on:
- GraphQL API development
- Django model relationships
- Automated task scheduling
- System administration with cron jobs