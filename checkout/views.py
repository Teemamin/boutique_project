from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm

# Create your views here.


def checkout(request):
    bag = request.session.get('bag', {})
    # having the if bag statemt will prevent the
    # user frm accessing /checkout manually
    if not bag:
        messages.error(request, 'There is nothing in your bag')
        return redirect(reverse('products'))
    order_form = OrderForm()
    # OrderForm is the instance of our form.py
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form
    }
    return render(request, template, context)

