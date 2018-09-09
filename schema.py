from graphene import ObjectType, String

class Query(ObjectType):
  hello = String(name=String(required=True))

  def resolve_hello(self, info, name):
    return 'Hello %s!' % name
