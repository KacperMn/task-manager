from django import forms
from .models import Task, Category, Schedule, ScheduleMoment
from django.forms.models import inlineformset_factory

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'schedule']
        
    def __init__(self, desk=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if desk:
            self.fields['category'].queryset = Category.objects.filter(desk=desk)
        # Make schedule field optional with a blank option
        self.fields['schedule'].required = False
        self.fields['schedule'].empty_label = "No Schedule"

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

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter schedule title'}),
        }

ScheduleMomentFormSet = inlineformset_factory(
    Schedule,
    ScheduleMoment,
    fields=('day_of_week', 'time_of_day'),
    extra=1,  # Number of empty forms to display
    can_delete=True,  # Allow users to delete moments
    widgets={
        'day_of_week': forms.Select(attrs={'class': 'form-control'}),
        'time_of_day': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
    }
)