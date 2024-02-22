from django import forms
from .models import Site, Post
from crispy_forms.helper import FormHelper
from tinymce.widgets import TinyMCE


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['url']  # include the new fields


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'summary', 'user', 'date_published', 'site', 'link', 'image_path', 'topics', 'content']
        widgets = {
            'date_published': forms.DateTimeInput(),
            'tags': forms.CheckboxSelectMultiple(),
            'content': TinyMCE(),
        }
