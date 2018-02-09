from decimal import Decimal
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, m2m_changed, post_save

from products.models import Product
User = settings.AUTH_USER_MODEL


class CartManager(models.Manager):
    def new_or_get(self, request):
        """
            Create a new cart if user did not have or assign a user to an existing cart.
            :param request:
            :return:
        """
        cart_id = request.session.get('cart_id', None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated() and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = Cart.objects.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        """
            We create this manager to ensure both authenticated and guests can have carts.
            :param user:
            :return:
        """
        user_obj = None
        if user is not None:
            if user.is_authenticated():
                user_obj = user
        return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)   # to ensure both
    # authenticated and non authenticated users can create carts we set null and blank
    # to True
    products = models.ManyToManyField(Product, blank=True)  # to be able to have a blank
    #  cart we set blank = True
    subtotal = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)


def m2m_cart_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_clear' or action == 'post_remove' or action == 'post_add':
        products = instance.products.all()
        total = 0
        for item in products:
            total += item.price
            # To save a db trip. if its same, do not bother
            if instance.subtotal != total:
                instance.subtotal = total
                instance.save()


# This is the way to connect your signal to a many to many field. (m2m)
m2m_changed.connect(m2m_cart_receiver, sender=Cart.products.through)


@receiver(pre_save, sender=Cart)    # connect to pre save signal using this decorator
def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    if instance.subtotal > 0:
        instance.total = format((Decimal(instance.subtotal) + Decimal(1.08)), '.2f')
    else:
        instance.total = 0.00


# How to connect a signal manually
# pre_save.connect(pre_save_cart_receiver, sender=Cart)
