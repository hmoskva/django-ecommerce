from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

from .forms import ContactForm


def home(request):
    context = {
        'title': 'Home',
        'content': 'Welcome to the Home.',
    }
    # print(request.session.get('first_name', 'Unknown'))
    return render(request, 'home_page.html', context)


def about(request):
    context = {
        'title': 'About',
        'content': 'Welcome to the About.',
    }
    return render(request, 'home_page.html', context)


def contact(request):
    form = ContactForm(request.POST or None)
    context = {
        'title': 'Contact',
        'content': 'Contact Us.',
        'form': form,
    }
    if form.is_valid():
        print(form.cleaned_data)
        if request.is_ajax():
            return JsonResponse({'message': 'Thank you'})

    if form.errors:
        errors = form.errors.as_json()
        if request.is_ajax():
            return HttpResponse(errors, status=400, content_type='application/json')
            #  we use http response here cus of the .as_json method we e are already
            # using on the errors
    return render(request, 'contact/view.html', context)




