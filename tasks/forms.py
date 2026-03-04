from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Task, Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your@email.com',
            'autocomplete': 'email',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'category', 'deadline', 'priority', 'estimated_hours')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Complete essay draft',
                'autocomplete': 'off',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Optional',
            }),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['category'].empty_label = '— No category —'
        self.fields['category'].required = False
        self.fields['deadline'].required = False
        self.fields['estimated_hours'].required = False

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if not title:
            raise forms.ValidationError('Task title is required.')
        return title

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline is not None and deadline.year < 2000:
            raise forms.ValidationError('Please choose a realistic deadline date.')
        return deadline

    def clean_estimated_hours(self):
        estimated = self.cleaned_data.get('estimated_hours')
        if estimated is not None and estimated < 1:
            raise forms.ValidationError('Estimated hours must be at least 1.')
        return estimated


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Mathematics, Web Science',
                'autocomplete': 'off',
            })
        }
