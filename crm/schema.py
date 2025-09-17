import graphene
from graphene_django import DjangoObjectType
from crm.models import Order, Product, Customer
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from decimal import Decimal
import uuid


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Error Types
class ErrorType(graphene.ObjectType):
    field = graphene.String()
    message = graphene.String()


class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = graphene.List(CustomerType)
    all_orders = graphene.List(OrderType)
    all_products = graphene.List(ProductType)
    customer = graphene.Field(CustomerType, id=graphene.Int())
    order = graphene.Field(OrderType, id=graphene.Int())
    product = graphene.Field(ProductType, id=graphene.Int())
    low_stock_products = graphene.List(ProductType)

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.all()

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_low_stock_products(self, info):
        return Product.objects.filter(stock__lt=10)


# Utility functions for validation
def validate_phone_format(phone):
    """Validate phone format: +1234567890 or 123-456-7890"""
    if not phone:
        return True
    pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
    return bool(re.match(pattern, phone))


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(ErrorType)

    def mutate(self, info, input):
        errors = []
        
        # Validate email format
        try:
            validate_email(input.email)
        except ValidationError:
            errors.append(ErrorType(field="email", message="Invalid email format"))
        
        # Check email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append(ErrorType(field="email", message="Email already exists"))
        
        # Validate phone format
        if input.phone and not validate_phone_format(input.phone):
            errors.append(ErrorType(field="phone", message="Invalid phone format. Use +1234567890 or 123-456-7890"))
        
        if errors:
            return CreateCustomer(customer=None, message="Validation failed", errors=errors)
        
        # Split name into first_name and last_name
        name_parts = input.name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        try:
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=input.email,
                phone=input.phone or ''
            )
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                errors=[]
            )
        except Exception as e:
            return CreateCustomer(
                customer=None,
                message=f"Failed to create customer: {str(e)}",
                errors=[ErrorType(field="general", message=str(e))]
            )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    message = graphene.String()

    def mutate(self, info, input):
        created_customers = []
        errors = []
        
        with transaction.atomic():
            for i, customer_data in enumerate(input):
                try:
                    # Validate email format
                    try:
                        validate_email(customer_data.email)
                    except ValidationError:
                        errors.append(f"Customer {i+1}: Invalid email format")
                        continue
                    
                    # Check email uniqueness
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Customer {i+1}: Email already exists")
                        continue
                    
                    # Validate phone format
                    if customer_data.phone and not validate_phone_format(customer_data.phone):
                        errors.append(f"Customer {i+1}: Invalid phone format")
                        continue
                    
                    # Split name into first_name and last_name
                    name_parts = customer_data.name.strip().split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                    
                    customer = Customer.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        email=customer_data.email,
                        phone=customer_data.phone or ''
                    )
                    created_customers.append(customer)
                    
                except Exception as e:
                    errors.append(f"Customer {i+1}: {str(e)}")
        
        success_count = len(created_customers)
        error_count = len(errors)
        message = f"Successfully created {success_count} customers. {error_count} failed."
        
        return BulkCreateCustomers(
            customers=created_customers,
            errors=errors,
            message=message
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()
    errors = graphene.List(ErrorType)

    def mutate(self, info, input):
        errors = []
        
        # Validate price is positive
        if input.price <= 0:
            errors.append(ErrorType(field="price", message="Price must be positive"))
        
        # Validate stock is non-negative
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            errors.append(ErrorType(field="stock", message="Stock cannot be negative"))
        
        if errors:
            return CreateProduct(product=None, message="Validation failed", errors=errors)
        
        try:
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            return CreateProduct(
                product=product,
                message="Product created successfully",
                errors=[]
            )
        except Exception as e:
            return CreateProduct(
                product=None,
                message=f"Failed to create product: {str(e)}",
                errors=[ErrorType(field="general", message=str(e))]
            )


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()
    errors = graphene.List(ErrorType)

    def mutate(self, info, input):
        errors = []
        
        # Validate customer exists
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            errors.append(ErrorType(field="customer_id", message="Invalid customer ID"))
            return CreateOrder(order=None, message="Validation failed", errors=errors)
        
        # Validate products exist and get them
        if not input.product_ids:
            errors.append(ErrorType(field="product_ids", message="At least one product must be selected"))
            return CreateOrder(order=None, message="Validation failed", errors=errors)
        
        products = []
        total_amount = Decimal('0.00')
        
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                products.append(product)
                total_amount += product.price
            except Product.DoesNotExist:
                errors.append(ErrorType(field="product_ids", message=f"Invalid product ID: {product_id}"))
        
        if errors:
            return CreateOrder(order=None, message="Validation failed", errors=errors)
        
        try:
            with transaction.atomic():
                # Generate unique order number
                order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                
                order = Order.objects.create(
                    customer=customer,
                    order_number=order_number,
                    total_amount=total_amount,
                    created_at=input.order_date if input.order_date else None
                )
                
                # Add products to the order
                order.products.set(products)
                
            return CreateOrder(
                order=order,
                message="Order created successfully",
                errors=[]
            )
        except Exception as e:
            return CreateOrder(
                order=None,
                message=f"Failed to create order: {str(e)}",
                errors=[ErrorType(field="general", message=str(e))]
            )


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    updated_products = graphene.List(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    count = graphene.Int()

    def mutate(self, info):
        # Query products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []
        
        # Update each product by incrementing stock by 10
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_products.append(product)
        
        count = len(updated_products)
        message = f"Successfully updated {count} low-stock products"
        
        return UpdateLowStockProducts(
            updated_products=updated_products,
            success=True,
            message=message,
            count=count
        )


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)