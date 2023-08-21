from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rider.models import Rider


class RiderSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = Rider
        fields = ['id','user_id', 'email', 'role','pending_payment', 'first_name', 'last_name', 'current_onboard_status']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        first_name = self.context['request'].data.get('first_name', None)
        last_name = self.context['request'].data.get('last_name', None)
        email = self.context['request'].data.get('email', None)

        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name

        if email is not None:
            user.email = email

        try:
            user.save()
        except Exception as e:
            raise ValidationError(e)

        return super(RiderSerializer, self).update(instance, validated_data)
