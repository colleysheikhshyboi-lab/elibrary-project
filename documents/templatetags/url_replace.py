from django import template

register = template.Library()

@register.simple_tag
def url_replace(request, field, value):
    """
    Replace or add a query parameter in the current URL.
    Usage: {% url_replace request 'page' 2 %}
    To remove a parameter: {% url_replace request 'page' '' %}
    """
    dict_ = request.GET.copy()
    if value == '' or value is None:
        # Remove the field if value is empty
        if field in dict_:
            del dict_[field]
    else:
        dict_[field] = value
    return dict_.urlencode()

