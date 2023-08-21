from django.urls import path
from .views import (GetStripePublicKeyView,AttachPaymentMethodView,DetachPaymentMethodView,
GetPaymentToken,RetrievePaymentMethodView,ConfirmPaymentView,RetryPaymentView)

urlpatterns = [
    path("publickey",GetStripePublicKeyView.as_view(), name="get-public-key"),
    path("get-token",GetPaymentToken.as_view(),name="get-payment-token"),
    path("attach/paymentmethod",AttachPaymentMethodView.as_view(),name="attach-payment-method"),
    path("detach/paymentmethod/<str:payment_method_id>",DetachPaymentMethodView.as_view(),name="detach-payment-method"),
    path("retrieve/paymentmethod",RetrievePaymentMethodView.as_view(),name="retrieve-payment-method"),
    path("confirm/payment-intent",ConfirmPaymentView.as_view(),name="confirm-payment-view"),
    path("retry/payment",RetryPaymentView.as_view(),name="retry-payment-view"),


]
