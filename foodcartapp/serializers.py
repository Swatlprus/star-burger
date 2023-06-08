from rest_framework.serializers import ModelSerializer
from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


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
            'products',
        ]

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = super().create(validated_data)

        order_items = [
            OrderItem(
                product=product_data['product'],
                price=product_data['product'].price,
                quantity=product_data['quantity'],
                order=order,
            )
            for product_data in products_data
        ]

        OrderItem.objects.bulk_create(order_items)
        return order
