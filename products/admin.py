from django.contrib import admin
from .models import Product, Category

# Register your models here.


# the below two classes exteds the builtin admin
# and usuing the list_display frm django
# it tells the admin which fields to disply
# rembr to always register the classes
# nxt to their respective models

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )
    ordering = ('sku',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
