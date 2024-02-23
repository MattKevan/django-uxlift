from django import forms
from .models import Site, Post, Topic
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from tinymce.widgets import TinyMCE


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['url']  # include the new fields

class DateInput(forms.DateInput):
    input_type = 'date'
    
    def __init__(self, **kwargs):
        kwargs['format'] = '%Y-%m-%d'  # Ensure the format is applied
        super().__init__(**kwargs)

class PostEditForm(forms.ModelForm):
    
    topics = forms.ModelMultipleChoiceField(
            queryset=Topic.objects.all(),  # Correctly accessing the queryset
            widget=forms.SelectMultiple(attrs={'class': 'tailwind-classes'}),  # Applying Tailwind CSS classes
        )
    class Meta:
        model = Post
        fields = ['title', 'topics', 'date_published', 'link', 'image_path', 'site', 'user', 'description',  'content'  ]
        widgets = {
            'content': TinyMCE(),
            'tags_list': forms.TextInput(),
            'date_published': DateInput()
        }
        

