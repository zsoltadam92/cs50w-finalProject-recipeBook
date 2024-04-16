from django import template

register = template.Library()

@register.filter(name='repeat_star')
def repeat_star(value):
    try:
        value = int(value)  # Convert string to integer
    except ValueError:
        return ''  # Return an empty string if conversion fails
    return '★' * value
