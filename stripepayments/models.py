from django.db import models


class StripeCustomerManage(models.Manager):
    def get_customer_from_stripe_id(self,stripe_id):
        return self.filter(stripe_customer_id=stripe_id)



class StripeCustomer(models.Model):
    customer = models.OneToOneField(to="rider.Rider", on_delete=models.CASCADE, related_name="stripe_customer")
    stripe_customer_id = models.CharField(max_length=255, null=True)

    objects = StripeCustomerManage()