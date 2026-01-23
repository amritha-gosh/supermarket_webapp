from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_URLS = [
    '/select-store/',
    '/setup/seed-stores/', 
    '/admin/',
    '/static/',  # allows static assets to load
]

class StoreRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if not any(path.startswith(exempt) for exempt in EXEMPT_URLS):
            store_key = request.session.get('store_key')
            if not store_key:
                return redirect(reverse('select_store'))  # or just '/select-store/'

        return self.get_response(request)
