import django
from django import forms
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import render_to_string
from django_addanother.widgets import BaseRelatedWidgetWrapper


class SelectWithPop(forms.Select):
    template_name = 'forms/widgets/select_with_popup.html'


class MultipleSelectWithPop(forms.SelectMultiple):
    def render(self, name, *args, **kwargs):
        html = super(MultipleSelectWithPop, self).render(name, *args, **kwargs)
        popupplus = render_to_string("widget/forms/widget/select_with_popup.html", {'field': name})
        return html + popupplus


class MyBaseRelatedWidgetWrapper(BaseRelatedWidgetWrapper):
    template = 'forms/widgets/related_widget_wrapper.html'

    class Media:
        css = {
            'all': ('django_addanother/addanother.css',)
        }
        js = (
            'django_addanother/django_jquery.js',
            static('js/RelatedObjectLookups.js'),
            # 'admin/js/admin/RelatedObjectLookups.js',
        )
        if django.VERSION < (1, 9):
            # This is part of "RelatedObjectLookups.js" in Django 1.9
            js += ('admin/js/related-widget-wrapper.js',)


class AddAnotherWidgetWrapper(MyBaseRelatedWidgetWrapper):
    """Widget wrapper that adds an add-another button next to the original widget."""

    def __init__(self, widget, add_related_url, add_icon=None):
        super(AddAnotherWidgetWrapper, self).__init__(
            widget, add_related_url, None, add_icon, None
        )


class EditSelectedWidgetWrapper(MyBaseRelatedWidgetWrapper):
    """Widget wrapper that adds an edit-related button next to the original widget."""

    def __init__(self, widget, edit_related_url, edit_icon=None):
        super(EditSelectedWidgetWrapper, self).__init__(
            widget, None, edit_related_url, None, edit_icon
        )


class AddAnotherEditSelectedWidgetWrapper(MyBaseRelatedWidgetWrapper):
    """Widget wrapper that adds both add-another and edit-related button
    next to the original widget.
    """
