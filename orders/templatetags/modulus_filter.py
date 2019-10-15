from django import template

register = template.Library()


@register.filter
def filter_strings(value, arg):
    return processed_string
