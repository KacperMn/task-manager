from django import forms
from .models import Task, Category

class TaskForm(forms.ModelForm):
    # Hidden field to store selected template IDs
    selected_templates = forms.CharField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'manage-input', 
                'placeholder': 'Task Title'
            }),
            'description': forms.TextInput(attrs={
                'class': 'manage-input', 
                'placeholder': 'Task Description'
            }),
            'category': forms.Select(attrs={
                'class': 'manage-select'
            }),
        }
        
    def __init__(self, desk=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if desk:
            self.fields['category'].queryset = Category.objects.filter(desk=desk)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'manage-input', 
                'placeholder': 'Category Title',
                'required': True
            }),
            'description': forms.TextInput(attrs={
                'class': 'manage-input', 
                'placeholder': 'Category Description'
            }),
        }