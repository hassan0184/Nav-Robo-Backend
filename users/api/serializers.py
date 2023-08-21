from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.db import IntegrityError
from rider.models import Rider


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'email', 'password', 'role', 'first_name', 'last_name']
        extra_kwargs = {'role': {'required': True},
                        'first_name': {'required': True, 'allow_null': False, 'allow_blank': False},
                        'last_name': {'required': True, 'allow_null': False, 'allow_blank': False}
                        }

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")
        if validated_data['role'] == 2:
            Rider.objects.create(user=user)

        return user
