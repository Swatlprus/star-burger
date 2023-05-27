from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Product, Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    data = request.data
    if 'products' not in data.keys():
        content = {
            'error': 'products: Обязательное поле',
        }
        return Response(
            content,
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )
    elif not isinstance(data['products'], list):
        content = {
            'error': 'Ожидался list со значениями, но был получен str.',
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif data['products'] is None:
        content = {
            'error': 'products: это поле не может быть пустым.',
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif not data['products']:
        content = {
            'error': 'products: Этот список не может быть пустым',
        }
        return Response(
            content,
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

    order_create, created = Order.objects.get_or_create(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phonenumber=data['phonenumber'],
        address=data['address'],
    )
    if not created:
        return
    for item in data['products']:
        order_create.items.create(
            product=Product.objects.get(pk=item['product']),
            quantity=item['quantity'],
        )
    return Response({})
