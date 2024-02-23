from django import forms
from .models import Site, Post, Topic
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from tinymce.widgets import TinyMCE


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['url']  # include the new fields


class PostEditForm(forms.ModelForm):
    
    topics = forms.ModelMultipleChoiceField(
            queryset=Topic.objects.all(),  # Correctly accessing the queryset
            widget=forms.SelectMultiple(attrs={'class': 'tailwind-classes'}),  # Applying Tailwind CSS classes
        )
    class Meta:
        model = Post
        fields = ['title', 'description', 'summary', 'user', 'date_published', 'site', 'link', 'image_path', 'content', 'tags_list', 'topics']
        widgets = {
            'date_published': forms.DateInput(),
            'content': TinyMCE(),
            'tags_list': forms.TextInput(),
        }
        

