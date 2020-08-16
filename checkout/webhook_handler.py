from django.http import HttpResponse
from .models import Order, OrderLineItem
from products.models import Product

import json
import time
"""
 Webhooks are like the signals django sends each time
 a model is saved or deleted.Except that they're sent
 securely from stripe to a URL we specify.

 The init method of the class is a setup method that's
 called every time an instance of the class is created.
 For us we're going to use it to assign the request as an
 attribute of the class just in case we need to access any
 attributes of the request coming from stripe.

 for each type of webhook we want a difrnt method to handle
 it,which makes it easier to manage
"""


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        it takes the event stripe is sending us and simply
        return an HTTP response indicating it was received.
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        -payment intent is saved in a key called event.data.object
        """
        intent = event.data.object
        # all the var with intent. are accessing the
        # weebhook(paymentintent) recived in this view
        # d weebhook(paymentintent succeeded)has all the customer info
        # we are ensuring that we get the user details in db incase
        # there was some error or the form wasnt submited at chkout
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)
        # to ensure the data is in the same form as what we want in our database.
        # I'll replace any empty strings in the shipping details with none.
        # Since stripe will store them as blank strings which is not the same
        # as the null value we want in the database.
        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None
        # see note for more explanations
        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    # iexact match to make it exact match but
                    # case insensitive
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

# to create a url for the webhook:
# technically you can put it anywhere
# but we are putting the url in
# urls.py of checkoutapp
# see notes for how to connect
# stripe url
