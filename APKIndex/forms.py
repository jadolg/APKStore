from django import forms

class SearchForm(forms.Form):
    asearch = forms.CharField(label='Buscar:',widget=forms.TextInput(attrs={'size':'50'}))

