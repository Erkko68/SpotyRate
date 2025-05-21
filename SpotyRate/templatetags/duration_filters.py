from django import template

register = template.Library()

@register.filter
def format_duration(ms):
    """Converts milliseconds to MM:SS (e.g., 3:45)."""
    if not ms:
        return "0:00"
    seconds = int(ms / 1000)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"

@register.filter
def format_iso_duration(ms):
    """Converts milliseconds to ISO 8601 duration (e.g., PT3M45S)."""
    if not ms:
        return "PT0S"
    seconds_total = int(ms / 1000)
    minutes = seconds_total // 60
    seconds = seconds_total % 60

    duration = "PT"
    if minutes > 0:
        duration += f"{minutes}M"
    if seconds > 0 or minutes == 0:
        duration += f"{seconds}S"
    return duration
