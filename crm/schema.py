import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Order, Product


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


class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_orders = graphene.List(OrderType)
    all_products = graphene.List(ProductType)
    customer = graphene.Field(CustomerType, id=graphene.Int())
    order = graphene.Field(OrderType, id=graphene.Int())
    product = graphene.Field(ProductType, id=graphene.Int())
    low_stock_products = graphene.List(ProductType)

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


class CreateCustomer(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()
        address = graphene.String()

    customer = graphene.Field(CustomerType)

    def mutate(self, info, first_name, last_name, email, phone=None, address=None):
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone or '',
            address=address or ''
        )
        customer.save()
        return CreateCustomer(customer=customer)


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
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)