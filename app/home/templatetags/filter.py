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
    return contains_in in str(value)


@register.filter(name='split')
def split(value, separator_with_idx):
    separator = separator_with_idx.split(':')[0]
    idx = separator_with_idx.split(':')[1]
    return value.split(separator)[idx]
