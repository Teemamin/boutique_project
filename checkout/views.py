from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.contexts import bag_contents

import stripe
# Create your views here.


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
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


