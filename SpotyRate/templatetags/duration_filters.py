from django import template

register = template.Library()

@register.filter
def format_duration(ms):
    if not ms:
        return "0:00"
    seconds = int(ms / 1000)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"