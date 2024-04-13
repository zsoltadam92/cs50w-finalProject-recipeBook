from django import forms
from .models import Recipe,Category

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'serving', 'preparation_time', 'difficulty', 'ingredients', 'preparation','image','categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'serving': forms.NumberInput(attrs={'class': 'form-control'}),
            'preparation_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control','rows': 5, 'placeholder': 'Enter each ingredient on a new line.'}),
            'preparation': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'categories': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.all()
