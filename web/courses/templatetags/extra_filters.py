from django import template

register = template.Library()


@register.filter(name='call')
def call(func, arg):
    return func(arg)
