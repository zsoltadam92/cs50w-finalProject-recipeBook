from django import template

register = template.Library()

@register.filter
def format_quantity(value):
    try:
        value = float(value)
        if value.is_integer():
            return int(value)
        else:
             return f"{value:.2f}"
    except ValueError:
        return value
