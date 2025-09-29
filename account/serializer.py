from django.core.validators import RegexValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    password1 = serializers.CharField(max_length=20, write_only=True, style={'input_type': 'password', 'placeholder': 'Password'})
    password2 = serializers.CharField(max_length=20, write_only=True, style={'input_type': 'password', 'placeholder': 'Password'})

    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        if password1 != password2:
            raise serializers.ValidationError('Passwords do not match')
        return attrs

    def create(self, validated_data):
        phone = validated_data.get('phone')
        password = validated_data.get('password1')
        user = User.objects.create(phone=phone, password=password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Phone number required'
        },
        validators=[
            RegexValidator(
                regex=r'^09\d{9}$',
                message='Phone number must be entered in the format: ',
                code='invalid'
            )
        ]
    )
    def validate(self, attrs):
        phone = attrs.get('phone')
        user = User.objects.get(phone=phone)
        attrs['user'] = user
        return attrs

    def validate_phone(self, value):
        try:
            user = User.objects.filter(phone=value).first()
            return user.phone
        except User.DoesNotExist:
            raise serializers.ValidationError('Phone number not found!')



class OtpVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{4}$'
            )
        ]
    )
