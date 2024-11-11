
from django import forms
from .models import Usuario, Casillero
from django.core.exceptions import ValidationError

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario

        fields = ['name', 'email']

class CasilleroPasswordForm(forms.ModelForm):
    class Meta:
        model = Casillero
        fields = ['password']  # Campo de contraseña
    
    nuevo_usuario_id = forms.ModelChoiceField(queryset=Usuario.objects.all(), required=False, label="Nuevo Usuario")

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # Verifica que la contraseña tenga exactamente 4 dígitos numéricos entre 1 y 6
        if len(password) != 4 or not password.isdigit():
            raise ValidationError('La contraseña debe ser un número de 4 dígitos.')

        # Verifica que los dígitos estén entre 1 y 6
        if any(int(digit) not in range(1, 7) for digit in password):
            raise ValidationError('La contraseña debe estar compuesta solo por números entre 1 y 6.')

        return password