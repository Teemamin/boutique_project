from django.shortcuts import render, redirect

# Create your views here.


def view_bag(request):
    """A view for the shopping bag"""
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    #  we need to convert it to an integer since it'll come from
    #  the template as a string.
    quantity = int(request.POST.get('quantity'))
    #  get the redirect URL from the form so we know where to
    #  redirect once the process here is finished.
    redirect_url = request.POST.get('redirect_url')
    #  using the HTTP session while the user browses the site
    #  and adds items to be purchased.By storing the shopping bag
    #  in the session.we can keep track of thr purchase per session
    #  it chks to see if the var bag already exisit in the session
    #  if not it will initialze it as an empty dict
    bag = request.session.get('bag', {})
    # If the item is already in the bag in other words
    # if there's already a key in the bag dictionary matching this product id.
    # Then I'll increment its quantity accordingly.else add the item n quantity
    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        bag[item_id] = quantity
    # this inputs the bag var into the session var
    request.session['bag'] = bag
    print(request.session['bag'])
    return redirect(redirect_url)
