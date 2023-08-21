from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from NavRobo.settings.base import STRIPE_PUBLISHABLE_KEY
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView
from .serializers import (AttachPaymentMethodSerializer)
from rest_framework import status
from .services.stripe import (get_payment_token, deatach_payment_method_of_user, retrieve_paymentmethod, get_stripe_customer_id,
                              create_paymentintent)


class GetStripePublicKeyView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'public key': STRIPE_PUBLISHABLE_KEY})


class GetPaymentToken(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'payment_method_id': get_payment_token()})


class AttachPaymentMethodView(CreateAPIView):
    serializer_class = AttachPaymentMethodSerializer


class DetachPaymentMethodView(APIView):
    def delete(self, request, *args, **kwargs):
        payment_method_id = kwargs.get('payment_method_id')
        deatach_payment_method_of_user(payment_method_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RetrievePaymentMethodView(APIView):
    def get(self, request, *args, **kwargs):
        local_user = self.request.user.rider
        stripe_customer_id = get_stripe_customer_id(local_user)
        return Response(retrieve_paymentmethod(stripe_customer_id))


class ConfirmPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        amount = request.data['amount']
        payment_method = request.data['payment_method']
        local_user = self.request.user.rider
        customer_id = get_stripe_customer_id(local_user)
        return Response(create_paymentintent(amount, payment_method, customer_id,local_user))

class RetryPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        
        local_user = self.request.user.rider
        amount = local_user.pending_payment
        if amount>0:
            local_user.is_pending_payment=False
            local_user.pending_payment=0
            local_user.save()
            customer_id = get_stripe_customer_id(local_user)
            retrieve_pm_id = retrieve_paymentmethod(customer_id)
            payment_method=retrieve_pm_id.data[0].get('id')
            return Response(create_paymentintent(amount, payment_method, customer_id,local_user))
        else:
            return Response("You don't have any due payment",status=status.HTTP_200_OK)
            
            
