from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    name = 'checkout'

# this lets django know that we have a signal
#  module with some listners in it


def ready(self):
    import checkout.signals