from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import Producto, Marca, Compra

# Formulario para la creación o edición de un Producto
class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = ['marca', 'nombre', 'modelo', 'unidades', 'precio', 'vip']

# Formulario de inicio de sesión
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    next = forms.CharField(widget=forms.HiddenInput, initial="/")

# Formulario para el registro de un nuevo usuario
class SignInForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Formulario para la creación de una nueva Compra
class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['producto', 'unidades', 'importe']

class FormBuscarProducto(forms.Form):
    texto = forms.CharField(required=False, widget=forms.TextInput({'class': 'form-control', 'placeholder': 'Buscar ...'}))
    marca = forms.ModelMultipleChoiceField(required=False, queryset=Marca.objects.all(),
                                           widget=forms.CheckboxSelectMultiple)