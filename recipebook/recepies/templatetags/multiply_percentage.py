from django import template

register = template.Library()

@register.filter
def multiply_percentage(value, total):
    try:
        return f"{(int(value) / int(total) * 100) if total > 0 else 0}%"
    except (ValueError, TypeError):
        return "0%"
