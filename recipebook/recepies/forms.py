from django import forms
from .models import Recipe, Category, Comment

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'serving', 'preparation_time', 'difficulty', 'raw_ingredients', 'preparation', 'image', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'serving': forms.NumberInput(attrs={'class': 'form-control'}),
            'preparation_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'raw_ingredients': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter ingredients freely. E.g., 2 eggs, 1 cup sugar...'}),
            'preparation': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter step by step preparation.'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'categories': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)
        # A kategóriák querysetjének beállítása
        self.fields['categories'].queryset = Category.objects.all()

    def save(self, commit=True):
        instance = super(RecipeForm, self).save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()  # Menti a ManyToMany kapcsolatokat
        return instance



class RatingForm(forms.Form):
    ratings = forms.ChoiceField(choices=[(str(i), str(i) + ' csillag') for i in range(1, 6)])

    def save(self, recipe_id):
        recipe = Recipe.objects.get(id=recipe_id)
        recipe.update_rating(int(self.cleaned_data['ratings']))


# class AddComment(forms.Form):
#     comment = forms.CharField(
#         label="",
#         widget=forms.Textarea(attrs={'placeholder': 'Write a comment', 'class': 'form-control form-group'})
#     )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Write a comment', 'class': 'form-control form-group'})
        }