import random
import os

from django.db import models
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.db.models import Q


def get_filename_ext(filepath):
    """
        Method to split file path into corresponding name and extension
    """
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    """
        Method to customize filename using random number and file extension
    """
    new_file_name = random.randint(1, 8679876779)
    name, ext = get_filename_ext(filename)
    final_file_name = '{new_file_name}{ext}'.format(new_file_name=new_file_name, ext=ext)
    return 'products/{new_file_name}/{final_file_name}'.format(
        new_file_name=new_file_name, final_file_name=final_file_name)


class ProductQuerySet(models.query.QuerySet):
    # To make queries like Products.objects.all().featured() possible
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        lookups = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(price__icontains=query) |
            Q(tags__title__icontains=query)
        )
        return self.filter(lookups).distinct()


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def featured(self):
        """
            Custom manager method to return only featured products
        """
        return self.get_queryset().featured()

    def all(self):
        """
            Overriding the all method of the manager to return only active products
        """
        return self.get_queryset().active()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)


class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2, default=39.99)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        # return '/products/{slug}/'.format(slug=self.slug)
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def name(self):
        """
            With the property tag above, i can do sth like instance.name and it
            will return the title even though it is not part of the model fields.
        """
        return self.title
