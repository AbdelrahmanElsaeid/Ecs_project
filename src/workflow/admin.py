from django.contrib import admin
from .models import Node, NodeType ,Graph, Token,Workflow

# Register your models here.

admin.site.register(Node)
admin.site.register(NodeType)
admin.site.register(Graph)
admin.site.register(Token)
admin.site.register(Workflow)




