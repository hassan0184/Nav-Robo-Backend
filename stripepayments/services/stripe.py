from NavRobo.settings.base import STRIPE_SECRET_KEY
import stripe
import datetime
from stripepayments.models import StripeCustomer
from rest_framework.exceptions import ValidationError
from rider.models import TransactionHistory

def retrieve_paymentmethod(stripe_customer_id):
        stripe.api_key = STRIPE_SECRET_KEY
        try:
            return stripe.Customer.list_payment_methods(
            stripe_customer_id,
            type="card",
            )
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(e.user_message)

def create_stripe_customer(name,email):
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe.Customer.create(name=name, email=email)

def save_stripe_customer_obj_locally(local_user,stripe_customer_obj): 
   return StripeCustomer.objects.create(customer=local_user, stripe_customer_id=stripe_customer_obj.id)

def get_stripe_customer_id(local_user):
    stripe_customer_obj = StripeCustomer.objects.filter(customer=local_user).first()
    if not stripe_customer_obj:
        stripe_customer_obj = create_stripe_customer(local_user.username,local_user.email)
        save_stripe_customer_obj_locally(local_user, stripe_customer_obj)
        return stripe_customer_obj.id
    else:
        return stripe_customer_obj.stripe_customer_id

def update_stripe_customer_invoice_settings(stripe_customer_id, updation_fields):
    try:
        stripe.api_key = STRIPE_SECRET_KEY
        return stripe.Customer.modify(stripe_customer_id, invoice_settings=updation_fields,)
    except stripe.error.InvalidRequestError as e:
        raise ValidationError(e.user_message)

def attach_payment_method_to_user(stripe_customer_id, payment_method_token):
    stripe.api_key = STRIPE_SECRET_KEY
    payment=retrieve_paymentmethod(stripe_customer_id)
    if payment:

        output =stripe.PaymentMethod.attach(payment_method_token,customer=stripe_customer_id,)
        deatach_payment_method_of_user(payment.data[0].id)
        updation_fields = {
            "default_payment_method":payment_method_token
        }
        update_stripe_customer_invoice_settings(stripe_customer_id, updation_fields)

    else:
        output =stripe.PaymentMethod.attach(payment_method_token,customer=stripe_customer_id,)
        updation_fields = {
            "default_payment_method":payment_method_token
        }
        update_stripe_customer_invoice_settings(stripe_customer_id, updation_fields)


def get_payment_token():
        
        stripe.api_key = STRIPE_SECRET_KEY
        try:
            payment_method=stripe.PaymentMethod.create(
            type="card",
            card={
                "number": "6200000000000005",
                "exp_month": 8,
                "exp_year": 2023,
                "cvc": "314",
            },
            )
            return payment_method.id
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(e.user_message)

def deatach_payment_method_of_user(payment_method_id):
    stripe.api_key = STRIPE_SECRET_KEY
    try:
     return stripe.PaymentMethod.detach(payment_method_id)
    except stripe.error.InvalidRequestError as e:
            raise ValidationError(e.user_message)

def create_paymentintent(amount,payment_method,customer_id,local_user):

        stripe.api_key = STRIPE_SECRET_KEY
        try:
                stripe_object=stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",
                payment_method_types=["card"],
                confirm=True,
                payment_method=payment_method,
                customer=customer_id,
                receipt_email=local_user.user.email,
                )
                TransactionHistory.objects.create(customer_id=stripe_object.customer,
                    amount=stripe_object.amount,
                    currency=stripe_object.currency,
                    payment_method_id=stripe_object.payment_method,
                    DateTime=datetime.datetime.now()
                    ,status=stripe_object.status)
                if stripe_object.status != "succeeded":
                    local_user.pending_payment=amount
                    local_user.is_pending_payment=True
                    local_user.save()
                         
                return stripe_object
                
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(e.user_message)

    






