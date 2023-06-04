from django import forms
import requests
from django.conf import settings
from geopy import distance
from django.db import transaction
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product
from foodcartapp.models import Restaurant
from foodcartapp.models import Order
from foodcartapp.models import RestaurantMenuItem
from distance.models import Place


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False) for restaurant in restaurants
        ]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    try:
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print('Oops. HTTP Error occured')
        print('Response is: {content}'.format(content=err.response.content))

    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


@transaction.atomic
def get_coordinates(address):
    place, created = Place.objects.get_or_create(address=address)

    if not created:
        return place.lat, place.lon

    yandex_geo_key = settings.YANDEX_GEO_KEY
    lat, lon = fetch_coordinates(yandex_geo_key, address)
    place.lat = lat
    place.lon = lon
    place.save()
    return lat, lon


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    order_items = Order.objects.count_price()\
        .exclude(status='Completed')\
        .prefetch_related('items')\
        .prefetch_related('items__product')

    restaurant_menu_items = RestaurantMenuItem.objects\
        .filter(availability=True)\
        .select_related('restaurant', 'product')

    for order in order_items:
        order.restaurants = set()

        for order_item in order.items.all():
            product_restaurants = [
                rest_item.restaurant for rest_item in restaurant_menu_items
                if order_item.product.id == rest_item.product.id
            ]

            if not order.restaurants:
                order.restaurants = set(product_restaurants)
                continue
            order.restaurants &= set(product_restaurants)
        for restaurant in order.restaurants:
            order_coords = get_coordinates(order.address)
            restaurant_coords = get_coordinates(restaurant.address)
            restaurant_distance = distance.distance(order_coords, restaurant_coords).km
            restaurant.name = f'{restaurant.name} - {round(restaurant_distance, 2)} км'

    return render(request, template_name='order_items.html', context={
        'order_items': order_items,
    })
