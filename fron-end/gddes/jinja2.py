import os
from django.templatetags.static import static
from django.urls import reverse, NoReverseMatch
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)

    def url_for(endpoint, **kwargs):
        if endpoint == 'static':
            filename = kwargs.get('filename') or kwargs.get('path', '')
            return static(filename)
        try:
            return reverse(endpoint, kwargs=kwargs)
        except NoReverseMatch:
            try:
                return reverse(endpoint)
            except NoReverseMatch:
                return f'/{endpoint}/' if not endpoint.startswith('/') else endpoint

    env.globals.update({
        'static': static,
        'url_for': url_for,
    })
    return env
