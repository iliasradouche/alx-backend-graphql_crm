import graphene
from graphene_django import DjangoObjectType
from crm.models import Order
from crm.models import Product
from crm.models import Customer
from crm.schema import Query
from crm.schema import Mutation





class MainQuery(Query, graphene.ObjectType):
    pass


class MainMutation(Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=MainQuery, mutation=MainMutation)