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
