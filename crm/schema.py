import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Order


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'


class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_orders = graphene.List(OrderType)
    customer = graphene.Field(CustomerType, id=graphene.Int())
    order = graphene.Field(OrderType, id=graphene.Int())

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


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)