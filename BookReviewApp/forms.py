from django import forms
from .models import User, Book, Review

class LogonForm(forms.Form):
    class Meta:
        model = User
        fields = ['email', 'password']  #Fields the user can edit

    def clean(self):
        return self.cleaned_data

class RegisterForm(forms.Form):
    class Meta:
        model = User
        fields = ['name', 'email', 'password']  #Fields the user can edit

    def clean(self):
        # General sanitization for all string fields can be done here
        for name, value in self.cleaned_data.items():
            if isinstance(value, str):
                self.cleaned_data[name] = value.strip() # Strip leading/trailing whitespace

        return self.cleaned_data

class SearchForm(forms.Form):
    class Meta:
        model = Book
        fields = ['isbn', 'title', 'author']  #Fields the user can edit

    def clean(self):
        return self.cleaned_data

class ReviewForm(forms.Form):
    class Meta:
        model = Review
        fields = ['review', 'rating']  #Fields the user can edit

    def clean(self):
        return self.cleaned_data
