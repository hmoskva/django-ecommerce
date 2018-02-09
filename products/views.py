from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import Http404

from analytics.mixins import ObjectViewedMixin
from .models import Product

from carts.models import Cart


class ProductFeaturedListView(generic.ListView):
    # queryset = Product.objects.all()
    template_name = 'products/list.html'

    def get_queryset(self, *args, **kwargs):
        return Product.objects.all().featured()


class ProductFeaturedDetailView(generic.DetailView):
    template_name = 'products/featured-detail.html'
    context_object_name = 'featured_product'

    def get_queryset(self, *args, **kwargs):
        return Product.objects.featured()


class ProductListView(generic.ListView):
    queryset = Product.objects.all()
    template_name = 'products/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        request = self.request
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        context['cart'] = cart_obj
        return context


def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, 'products/list.html', context)


class ProductDetailView(generic.DetailView):
    # queryset = Product.objects.all()
    template_name = 'products/detail.html'

    # def get_context_data(self, *args, **kwargs):
    #     context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
    #     context['test'] = 'This  is a test'
    #     # print(context)
    #     return context

    def get_object(self, *args, **kwargs):
        # request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404('Product does not exist')
        return instance


class ProductDetailSlugView(ObjectViewedMixin, generic.DetailView):
    queryset = Product.objects.all()
    template_name = 'products/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        request = self.request
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        context['cart'] = cart_obj
        return context

    def get_object(self, *args, **kwargs):

        slug = self.kwargs.get('slug')
        # instance = get_object_or_404(Product, slug=slug, active=True)
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404('Product does not exist')
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug, active=True)
            instance = qs.first()
        except:
            raise Http404('Nothing here')
        # object_viewed_signal.send(instance.__class__, instance=instance,
        #                           request=self.request)
        return instance


# def product_detail_view(request, pk=None, *args, **kwargs):
#     """
#         There are different ways to get an item detail. Using a normal get,
#         using get_object_or_404, using queryset.exists etc. This view shows some.
#         commented obvs. So, there is a lot to choose from.
#     """
#     # way 1: does not handle case of non existence of product
#     # instance = Product.objects.get(pk=pk)
#
#     # way 2: handles case of non existence of product but cant set custom error message
#     # instance = get_object_or_404(Product, pk=pk)
#
#     # way 3: handles case of non existence of product and custom error message can be
#     # set in Http404 method.
#     # try:
#     #     instance = Product.objects.get(pk=pk)
#     # except Product.DoesNotExist:
#     #     raise Http404('Product Does not exist')
#     # except:
#     #     print('Nothing here')
#
#     # way 4: Also handles case of non existence of product and custom error message can be
#     # set in Http404 method.
#     # qs = Product.objects.filter(pk=pk)
#     # if qs.exists() and qs.count() == 1:
#     #     instance = qs.first()
#     # else:
#     #     raise Http404('Product does not exist')
#
#     # way 5: creating custom manager in models to handle queryset to return object
#     instance = Product.objects.get_by_id(pk)
#     if instance is None:
#         raise Http404('Product does not exist')
#
#     context = {
#         'object': instance
#     }
#     return render(request, 'products/detail.html', context)

