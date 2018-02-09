from django.shortcuts import render
from django.views import generic
from django.http import Http404
from products.models import Product


class SearchProductView(generic.ListView):
    template_name = 'search/view.html'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        query = request.GET.get('q', None)    # preferred to request.Get['q'] because this
        # returns an error if there is no key q in the dict.
        if query is not None:
            return Product.objects.search(query)
        return Product.objects.featured()

