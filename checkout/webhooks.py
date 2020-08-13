from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
# will make this view require a post request and will reject get requests.
from django.views.decorators.csrf import csrf_exempt
# CSRF exempt since stripe won't send a CSRF token like we'd normally need.

from checkout.webhook_handler import StripeWH_Handler

import stripe


@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe
      the code for this mostly comes frm
      stripe
    """
    # Setup
    # we use the wh_secret key n secrt key to verify that
    # the webhoock came frm stripe
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
         payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    print('success')
    return HttpResponse(status=200)

    # Set up a webhook handler
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions
    # the dictionaries keys will be the names of the webhooks
    # coming from stripe.While its values will be the actual
    # methods inside the handler.
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Get the webhook type from Stripe
    # gets the type of the event from stripe which will be stored
    # in a key called type.So this will return something like
    # payment intent.succeeded or payment intent.payment failed.
    event_type = event['type']

    # If there's a handler for it, get it from the event map
    # Use the generic one by default
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event
    response = event_handler(event)
    return response
    # return response to stripe
