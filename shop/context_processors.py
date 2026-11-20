
def cart_summary(request):
    cart = request.session.get("shopping_cart", {})

    cart_count = sum(cart.values())

    return {
        "cart_count": cart_count
    }
