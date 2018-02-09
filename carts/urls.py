from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.cart_home, name='home'),
    url(r'update/$', views.cart_update, name='update'),
    url(r'checkout/$', views.cart_checkout, name='checkout'),
    url(r'success/$', views.checkout_success, name='success'),

]