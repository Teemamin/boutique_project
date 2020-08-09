from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import messages
from products.models import Product
# Create your views here.


def view_bag(request):
    """A view for the shopping bag"""
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    product = Product.objects.get(pk=item_id)
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
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})
    # If the item is already in the bag in other words
    # if there's already a key in the bag dictionary matching this product id.
    # Then I'll increment its quantity accordingly.else add the item n quantity
    # if there is size
    if size:
        # If the item is already in the bag.
        if item_id in list(bag.keys()):
            # Then we need to check if another item of the same id and
            #  same size already exists.
            if size in bag[item_id]['items_by_size'].keys():
                # if so increment the quantity for that size
                bag[item_id]['items_by_size'][size] += quantity
            else:
                #  otherwise just set it equal to the quantity.
                bag[item_id]['items_by_size'][size] = quantity
        else:
            # If the items not already in the bag we just need to add it.
            #  But we're actually going to do it as a dictionary with a key
            #  of items_by_size.Since we may have multiple items with
            #  this item id. But different sizes.
            bag[item_id] = {'items_by_size': {size: quantity}}
    else:
        # if there's no size we run this logic.
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity
            messages.success(request, f'Added {product.name} to your bag')
    # this inputs the bag var into the session var
    request.session['bag'] = bag
    #  print(request.session['bag'])
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""

    quantity = int(request.POST.get('quantity'))
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})

    if size:
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
        else:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
    else:
        if quantity > 0:
            bag[item_id] = quantity
        else:
            bag.pop(item_id)

    request.session['bag'] = bag
    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""

    try:
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})

        if size:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
        else:
            bag.pop(item_id)

        request.session['bag'] = bag
        # Because this view will be posted to from a JavaScript function.
        # We want to return an actual 200 HTTP response.Implying that the
        #  item was successfully removed.
        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(status=500)