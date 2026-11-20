
from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.product_list, name="product_list"),

    path(
        "add-to-cart/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path("cart/", views.cart_view, name="cart"),

    path(
        "update-cart/<int:product_id>/",
        views.update_cart,
        name="update_cart"
    ),

    path(
        "remove-from-cart/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    path("checkout/", views.checkout, name="checkout"),

    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),
]
