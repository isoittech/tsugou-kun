from django import template

from home import constants

register = template.Library()


@register.filter(name='lookup')
def lookup(value, arg, default=""):
    if arg in value:
        return value[arg]
    else:
        return default


@register.filter(name='to_symbol')
def to_symbol(value):
    if value == constants.SANKA_MARU:
        return constants.SANKA_KIGOU_MARU
    elif value == constants.SANKA_SANKAKU:
        return constants.SANKA_KIGOU_SANKAKU
    elif value == constants.SANKA_BATSU:
        return constants.SANKA_KIGOU_BATSU
    else:
        return constants.SANKA_KIGOU_MINYUURYOKU


@register.filter(name='contains_in')
def contains_in(value, contains_in):
    print(value)
    return contains_in in str(value)
