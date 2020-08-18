from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        # __all__ means is called all
        # which will include all the fields
        fields = '__all__'
    # override the init method to make a couple changes to the fields.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        # usin list comprehension to loop tru categories
        # create a list of tuples of the friendly names associated
        # with their category ids.
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        # Now that we have the friendly names, let's update the category field
        # on the form.To use those for choices instead of using the id.
        self.fields['category'].choices = friendly_names
        # loop tru the fields and set css class to match d rest of the site
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
