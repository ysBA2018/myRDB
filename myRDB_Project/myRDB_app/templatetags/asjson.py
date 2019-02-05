from django import template
import simplejson
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def asjson(data):
    return mark_safe(simplejson.dumps(data))