from marshmallow import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Order, OrderItem


class PhoneNumberSerializer(serializers.Serializer):
    number = PhoneNumberField(region='RU')


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products'
        ]

    def validate_phonenumber(self, value):
        if not (PhoneNumberSerializer(data={"number": value})).is_valid():
            raise ValidationError('Введен некорректный номер телефона')
        return value
