from django.forms.widgets import ClearableFileInput
# note using 'as_' means we can call gettext_lazy() using
# _() it is effective as alias
from django.utils.translation import gettext_lazy as _


# CustomClearableFileInput inherits django builtin ClearableFileInput
class CustomClearableFileInput(ClearableFileInput):
    # we overwite the clear_checkbox_lable,initial_text,input_text
    # and templates with our own value
    clear_checkbox_label = _('Remove')
    initial_text = _('Current Image')
    input_text = _('')
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'