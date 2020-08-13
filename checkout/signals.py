from django.db.models.signals import post_save, post_delete
# this implies these signals are sent by django to the entire application
# after a model instance is saved and after it's deleted respectively.
from django.dispatch import receiver

from .models import OrderLineItem
"""
sender: parameters refer to the sender of the signal. In
our case OrderLineItem.
instance: The actual instance of the model that sent it.
created : A boolean sent by django referring to whether
this is a new instance or one being updated.
**kwargs:any keyword arguments.
"""


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.order.update_total()


@receiver(post_delete, sender=OrderLineItem)
def delete_on_save(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()


"""
 the post_save and post_delete are django's builtin signals
 that let user code get notified by Django itself of certain actions
 post_save : Sent after a model’s save() method is called.
 post_delete: Sent after a model’s delete() method or queryset’s delete()
  method is called.
  https://docs.djangoproject.com/en/3.0/topics/signals/
"""