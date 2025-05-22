from django import template
from account.models import User, GroupName
register = template.Library()

@register.filter
def group_name(client):
    try:
        return GroupName.objects.get(user=client).category
    except GroupName.DoesNotExist:
        return "N/A"

