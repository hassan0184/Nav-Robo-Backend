import requests
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework import status, exceptions, serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

# from django.contrib.auth.models import User
from users.models import User


class InActiveUser(AuthenticationFailed):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = "User is not Active, Please Confirm your Email."
    default_code = 'user_is_inactive'


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    """
    This Custom Serializer Overrides the 'TokenObtainSerializer' validate method in not a traditional way.
    It does the same things except a different Response for Inactive Users without calling Super()
    """
    default_error_messages = {
        'no_active_account': _('Invalid Credentials')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.EmailField()
        self.fields['role'] = serializers.IntegerField()

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        role = self.context['request'].data['role']
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        custom_user = User.objects.filter(email=attrs[self.username_field], role=role)
        if custom_user and not custom_user.first().is_active:
            host = self.context['request'].get_host()
            protocol = "https://" if self.context['request'].is_secure() else "http://"
            url = f'{protocol}{host}/auth/users/resend_activation/'
            requests.post(url=url, data={"email": custom_user.first().email})
            raise InActiveUser()

        # if custom_user.first() is None:
        #     raise PermissionDenied
        self.user = authenticate(**authenticate_kwargs)
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )
        data = {}
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
