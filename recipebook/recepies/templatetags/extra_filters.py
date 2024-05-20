from django import template

register = template.Library()

@register.filter(name='repeat_star')
def repeat_star(value):
    try:
        value = int(value)  
    except ValueError:
        return '' 
    return '★' * value
