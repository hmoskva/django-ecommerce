"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from accounts.views import LoginView, guest_register, RegisterView
from addresses.views import checkout_address_create, checkout_address_use
from carts.views import cart_detail_api_view
from .views import home, about, contact

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^about/$', about, name='about'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^api/cart/$', cart_detail_api_view, name='api-cart'),
    url(r'^checkout/address/create/$', checkout_address_create,
        name='checkout_address_create'),
    url(r'^checkout/address/reuse/$', checkout_address_use,
        name='checkout_address_use'),
    url(r'^register/guest/$', guest_register, name='guest_register'),
    url(r'^logout/$', LogoutView.as_view(template_name='home_page.html'), name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^admin/', admin.site.urls),
    url(r'^products/', include('products.urls', namespace='products')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^cart/', include('carts.urls', namespace='cart')),

    ]

# not for production. do not do this in production!
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)