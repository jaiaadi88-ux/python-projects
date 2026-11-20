
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import Product, Order, OrderItem


def product_list(request):
    products = Product.objects.filter(
        is_available=True,
        stock__gt=0
    )

    return render(
        request,
        "shop/product_list.html",
        {"products": products}
    )


def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(
            Product,
            id=product_id,
            is_available=True
        )

        cart = request.session.get("shopping_cart", {})
        product_id = str(product.id)

        current_quantity = cart.get(product_id, 0)

        if current_quantity < product.stock:
            cart[product_id] = current_quantity + 1

        request.session["shopping_cart"] = cart

    return redirect("shop:product_list")


def update_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(
            Product,
            id=product_id
        )

        cart = request.session.get("shopping_cart", {})
        product_id = str(product.id)

        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            quantity = 1

        if quantity <= 0:
            cart.pop(product_id, None)
        elif product.is_available:
            cart[product_id] = min(quantity, product.stock)

        request.session["shopping_cart"] = cart

    return redirect("shop:cart")


def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get("shopping_cart", {})
        cart.pop(str(product_id), None)
        request.session["shopping_cart"] = cart

    return redirect("shop:cart")


def cart_view(request):
    cart = request.session.get("shopping_cart", {})

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)

            subtotal = product.price * quantity
            total += subtotal

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

        except Product.DoesNotExist:
            continue

    return render(
        request,
        "shop/cart.html",
        {
            "cart_items": cart_items,
            "total": total
        }
    )


def checkout(request):
    cart = request.session.get("shopping_cart", {})

    if not cart:
        return redirect("shop:product_list")

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(
                id=product_id,
                is_available=True
            )

            if quantity <= 0 or quantity > product.stock:
                return redirect("shop:cart")

            subtotal = product.price * quantity
            total += subtotal

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

        except Product.DoesNotExist:
            return redirect("shop:cart")

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name", ""
        ).strip()

        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        if not all([customer_name, email, phone, address]):
            return redirect("shop:checkout")

        with transaction.atomic():

            for item in cart_items:
                product = Product.objects.get(
                    id=item["product"].id
                )

                if (
                    not product.is_available
                    or product.stock < item["quantity"]
                ):
                    return redirect("shop:cart")

            order = Order.objects.create(
                customer_name=customer_name,
                email=email,
                phone=phone,
                address=address,
                total_amount=total
            )

            for item in cart_items:
                product = Product.objects.get(
                    id=item["product"].id
                )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=item["quantity"],
                    subtotal=item["subtotal"]
                )

                product.stock -= item["quantity"]
                product.save()

        request.session["shopping_cart"] = {}

        return redirect(
            "shop:order_success",
            order_id=order.id
        )

    return render(
        request,
        "shop/checkout.html",
        {
            "cart_items": cart_items,
            "total": total
        }
    )


def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id
    )

    return render(
        request,
        "shop/order_success.html",
        {"order": order}
    )
