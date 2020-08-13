from django.http import HttpResponse
"""
 Webhooks are like the signals django sends each time
 a model is saved or deleted.Except that they're sent
 securely from stripe to a URL we specify.

 The init method of the class is a setup method that's
 called every time an instance of the class is created.
 For us we're going to use it to assign the request as an
 attribute of the class just in case we need to access any
 attributes of the request coming from stripe.
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
            content=f'Webhook received: {event["type"]}',
            status=200)
