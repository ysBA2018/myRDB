from django import template

register = template.Library()


@register.filter
def getdictitem(dictionary, key):
    return dictionary.get(key)
