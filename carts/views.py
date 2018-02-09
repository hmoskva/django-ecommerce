from django.shortcuts import render, redirect
from django.http import JsonResponse

from .models import Cart
from products.models import Product
from orders.models import Order
from billing.models import BillingProfile
from addresses.models import Address
from accounts.forms import LoginForm, GuestForm
from addresses.forms import AddressForm


def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{
        'id': x.id,
        'url': x.get_absolute_url(),
        'name': x.title,
        'desc': x.description,
        'price': x.price}
        for x in cart_obj.products.all()
    ]
    cart_data = {
        'products': products,
        'subtotal': cart_obj.subtotal,
        'total':cart_obj.total
    }
    return JsonResponse(cart_data)


def cart_home(request):
    context = {}
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    context['cart'] = cart_obj
    return render(request, 'carts/home.html', context)


def cart_update(request):
    product_id = request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print('Product no dey')
            return redirect('cart:home')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)   # How to remove from m2m relationship.
            added = False
        else:
            cart_obj.products.add(product_obj)  # How to add to a many to many field. Can also
        # do this by passing the product ID rather than product object itself.
            added = True
        request.session['cart_items'] = cart_obj.products.count()
        # return redirect(product_obj.get_absolute_url())

        if request.is_ajax():
            json_data = {
                'added': added,
                'removed': not added,
                'cartCount': cart_obj.products.count(),
            }

            return JsonResponse(json_data)
            # return JsonResponse(json_data, status=400) emulatng a 400 error to
            # test jquery confirm.
    return redirect('cart:home')


def cart_checkout(request):
    context = {}
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:  # check if its a new cart
        redirect('cart:home')

    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()

    billing_address_id = request.session.get('billing_address_id', None)
    shipping_address_id = request.session.get('shipping_address_id', None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    if billing_profile is not None:
        if request.user.is_authenticated():
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session['shipping_address_id']
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()

    if request.method == 'POST':
        is_done = order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            request.session['cart_items'] = 0
            del request.session['cart_id']
            return redirect('cart:success')

    context['billing_profile'] = billing_profile
    context['login_form'] = login_form
    context['guest_form'] = guest_form
    context['address_form'] = address_form
    context['object'] = order_obj
    context['address_qs'] = address_qs
    return render(request, 'carts/checkout.html', context)


def checkout_success(request):
    return render(request, 'carts/success.html')