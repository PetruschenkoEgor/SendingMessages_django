from django import template


register = template.Library()


@register.filter
def has_group(user, group_name):
    """ Фильтр по принадлежности к определенной группе пользователей """

    return user.groups.filter(name=group_name).exists()
