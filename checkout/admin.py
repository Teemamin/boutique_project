from django.contrib import admin
from .models import Order, OrderLineItem

# Register your models here.


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)
    """
        This inline item is going to allow us to add and
        edit line items in the admin right from inside the
        order model.So when we look at an order.
        We'll see a list of editable line items on the same page.
        And to add it to the order admin interface.
        We just need to add the inlines option in the order admin class.
        like so: inlines = (OrderLineItemAdminInline)
    """


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', 'original_bag', 'stripe_pid')
    #  used fields to specify the order of the fields in the admin interface
    # user_profile here refers to d user_profile field in order model
    fields = ('order_number', 'user_profile', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total', 'original_bag', 'stripe_pid')
    # used list display to restrict the columns that show up
    # in the order list to only a few key items.
    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total',)

    # sort by most recent date
    ordering = ('-date',)


admin.site.register(Order, OrderAdmin)
# did not register the OrderLineItem model.
# Since it's accessible via the inline on the order model.
