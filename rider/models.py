from django.conf import settings
from django.db import models
from stripepayments.models import StripeCustomer

class Rider(models.Model):
    """
    Profile model for the user - rider
    """

    class OnboardScreen(models.IntegerChoices):
        COMPLETED = 0
        PAGEONE = 1
        PAGETWO = 2
        PAGETHREE = 3

    current_onboard_status = models.IntegerField(
        choices=OnboardScreen.choices, default=OnboardScreen.PAGEONE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rider', default=None)
    pending_payment=models.FloatField(null=True,blank=True)
    is_pending_payment=models.BooleanField(default=False)

    def email(self):
        return self.user.email

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def role(self):
        return self.user.role
    def __str__(self):
        return self.user.email


class TransactionHistory(models.Model):
    customer_id = models.CharField(max_length=50)
    amount = models.IntegerField()
    currency = models.CharField(max_length=50)
    payment_method_id = models.CharField(max_length=50)
    DateTime = models.DateTimeField(blank=True, null=True)
    status=models.CharField(max_length=50)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        verbose_name_plural = "Transaction History"

    def save(self, *args, **kwargs):
        customer_object= StripeCustomer.objects.filter(stripe_customer_id=self.customer_id).first()
        self.rider=customer_object.customer
        super(TransactionHistory, self).save(*args, **kwargs)
    def __str__(self):
        return 'Transaction of {} with price {}'.format(self.rider.email(),self.amount)
