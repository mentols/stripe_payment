from django.contrib import admin
from payment.models import Item, Order, Tax, Discount, Content

AdminModels = [Item, Order, Tax, Discount, Content]
admin.site.register(AdminModels)




