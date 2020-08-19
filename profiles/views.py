from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import UserProfileForm
from checkout.models import Order


@login_required
def profile(request):
    """ Display the user's profile. """
    # current profile instance
    profile = get_object_or_404(UserProfile, user=request.user)
    # if request is post:create a new instance of d user profile
    # form usin the form data
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure\
                 the form is valid.')
    else:

        # populate the form with the current user info
        form = UserProfileForm(instance=profile)
    # usin d profile n  related name on the order model
    # to get user orders
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)


def order_history(request, order_number):
    # gets the order model n passes it the order # recived
    # in the view(argument)
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
        # since we are usin checkout_success template to render this
        # view d variable 'from_profile' allows us to  check in that
        # template if the user got there via the order history view.
    }

    return render(request, template, context)