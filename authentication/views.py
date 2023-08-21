from django.utils.timezone import now
from djoser.compat import get_user_email
from djoser.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from djoser import signals
from rest_framework.exceptions import ValidationError, PermissionDenied

from authentication.serializers import CustomTokenObtainPairSerializer, InActiveUser
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenViewBase
from djoser.views import UserViewSet


class CustomTokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.

    Returns HTTP 406 when user is inactive and HTTP 401 when login credentials are invalid or incase a role is invalid.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            raise InActiveUser()
        except TokenError:
            raise InvalidToken()

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomResetPasswordView(UserViewSet):
    """
    Override djoser default reset password confirm to change the response to now include the roles of the user
    who is resetting the password
    """

    def perform_create(self, serializer):
        user = serializer.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = {"user": user}
        to = [get_user_email(user)]
        try:
            if settings.SEND_ACTIVATION_EMAIL:
                settings.EMAIL.activation(self.request, context).send(to)
            elif settings.SEND_CONFIRMATION_EMAIL:
                settings.EMAIL.confirmation(self.request, context).send(to)
        except:
            pass

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)

        return Response(status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user(is_active=False)

        if not user:
            raise PermissionDenied("You have already activated your email")

        if not settings.SEND_ACTIVATION_EMAIL:
            raise ValidationError("unable to send activation email at this time. Try again later")

        try:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)
        except:
            raise ValidationError("unable to send activation email at this time. Try again later")
        return Response(status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        super(CustomResetPasswordView, self).reset_password(request, *args, **kwargs)

        return Response(status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [get_user_email(serializer.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        return Response(data={"role": serializer.user.role})
