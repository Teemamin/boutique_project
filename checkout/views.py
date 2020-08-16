from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe
import json
# Create your views here.

# b4 we call the confirmcard payment method in
# strip_elements.js we will make a post rqst to
# this view n give it d clientsecret frm d paymentintent
@require_POST
def cache_checkout_data(request):
    # see notes for explanation
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        bag = request.session.get('bag', {})
        # collecting the form field data manually below(form_data)
        # so as to skip the save info chkbox,cos it doesn't have a
        # field in our Order module
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # gets theform data above frm the post
        # and inputs it into our form.py for validatn
        order_form = OrderForm(form_data)
        # if the form is valid,save the order
        if order_form.is_valid():
            # used commit=false to prevent multiple save events in database
            order = order_form.save(commit=False)
            # gets clientsecret id
            pid = request.POST.get('client_secret').split('_secret')[0]
            # adds the clientsecret id to order model stripe_pid field
            order.stripe_pid = pid
            # adds order shopping bag to order model original_bag field
            order.original_bag = json.dumps(bag)
            order.save()
            # see ur notes for further explanations
            for item_id, item_data in bag.items():
                try:
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
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our\
                        database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))
            # if a user wants to save their info we will redirect them
            # to checkout success page and pass in order # as argument
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success',
                            args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:

        bag = request.session.get('bag', {})
        # having the if bag statemt will prevent the
        # user frm accessing /checkout manually
        if not bag:
            messages.error(request, 'There is nothing in your bag')
            return redirect(reverse('products'))
        # uses the functn imported frm context.py
        # to calculate grand total
        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        # multiply that by a hundred and round it to zero
        # decimal places using the round function.
        # Since stripe will require the amount to charge as an integer.
        stripe_total = round(total * 100)
        # sets the secret key on stripe
        stripe.api_key = stripe_secret_key
        # creates payment intent
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
        order_form = OrderForm()
        # OrderForm is the instance of our form.py

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }
    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    # gets the saveinfo details from session request
    # which was added above from the form post data
    save_info = request.session.get('save_info')
    # order_number recived in this functn is the 
    # arg passed frm chkout view:order.order_number
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')
    # if there is bag in session delete it
    # at this point order is done, bag is no longer
    # needed for this session
    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)


