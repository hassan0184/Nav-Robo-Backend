from django.db.models.signals import post_save
from django.dispatch import receiver
from NavRobo.settings.base import STRIPE_SECRET_KEY
from .models import Rider
import stripe
from  stripepayments.models import StripeCustomer


@receiver(post_save, sender=Rider)
def register_user_on_stripe(sender, instance, created, **kwargs):
    if created:
        stripe.api_key = STRIPE_SECRET_KEY
        stripe_customer_obj = stripe.Customer.create(name=instance.user.first_name, email=instance.user.email)
        StripeCustomer.objects.create(customer=instance, stripe_customer_id=stripe_customer_obj.id)