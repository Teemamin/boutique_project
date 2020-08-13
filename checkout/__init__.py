# to ensure our signals are working:
# we need to tell django the name of
# the default config class for the app
# Without this line in the innit file,
# django wouldn't know about our custom
# ready method (in app.py)so our signals wouldn't work.

default_app_config = 'checkout.apps.CheckoutConfig'
