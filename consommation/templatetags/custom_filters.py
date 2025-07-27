from django import template

register = template.Library()

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except:
        return None

@register.filter
def max(sequence):
    try:
        return max(sequence)
    except:
        return None

@register.filter
def diff(value, arg):
    """Soustrait deux nombres."""
    try:
        return float(value) - float(arg)
    except:
        return 0
    
@register.filter
def prev_value(values, index):
    try:
        index = int(index)
        if index > 0:
            return values[index - 1]
        return None
    except:
        return None
