from rest_framework.exceptions import ValidationError
from rest_framework import serializers
import stripe
from .services.stripe import (
    get_stripe_customer_id,
    attach_payment_method_to_user

)
class AttachPaymentMethodSerializer(serializers.Serializer):
    payment_method_token = serializers.CharField()

    def save(self, **kwargs):
        try:
            payment_method_token = self.validated_data.get('payment_method_token')
            local_user = self.context.get("request").user.rider
            stripe_customer_id = get_stripe_customer_id(local_user)
            attach_payment_method_to_user(stripe_customer_id,payment_method_token)
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(e.user_message)
        except Exception as e:
            raise ValidationError(e)
