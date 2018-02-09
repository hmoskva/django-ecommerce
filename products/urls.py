from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ProductListView.as_view(), name='products_home'),
    url(r'^(?P<slug>[\w-]+)/$', views.ProductDetailSlugView.as_view(),
        name='product_detail'),
]