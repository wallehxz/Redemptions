from django import template

register = template.Library()

@register.filter
def default_dash(value):
    return value if value is not None else "--"