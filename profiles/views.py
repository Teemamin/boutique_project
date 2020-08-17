from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import UserProfile
from .forms import UserProfileForm


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