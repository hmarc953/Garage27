from datetime import date
from django import forms
from hashlib import sha256

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from .models import CorreoAutorizado



SERVICIOS = [
    ('', 'Seleccioná un servicio'),
    ('detailing', 'Detailing integral'),
    ('pulido', 'Pulido profesional'),
    ('ceramico', 'Tratamiento cerámico'),
    ('motor', 'Limpieza de motor'),
    ('personalizacion', 'Personalización estética'),
]

HORARIOS = [
    ('', 'Seleccioná un horario'),
    ('09:00', '09:00'),
    ('11:00', '11:00'),
    ('14:00', '14:00'),
    ('16:00', '16:00'),
]

class TurnoForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre y apellido',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: Juan Pérez'
        }),
        error_messages={
            'required': 'Ingresá tu nombre y apellido.'
        }
    )

    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ej: juan@email.com'
        }),
        error_messages={
            'required': 'Ingresá tu correo electrónico.',
            'invalid': 'Ingresá un correo electrónico válido.'
        }
    )

    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 11 1234 5678'
        }),
        error_messages={
            'required': 'Ingresá tu teléfono.'
        }
    )

    vehiculo = forms.CharField(
        label='Marca y modelo',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: BMW Serie 3'
        }),
        error_messages={
            'required': 'Ingresá la marca y modelo de tu vehículo.'
        }
    )

    patente = forms.CharField(
        label='Patente',
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: AB123CD'
        })
    )

    servicio = forms.ChoiceField(
        label='Servicio',
        choices=SERVICIOS,
        error_messages={
            'required': 'Seleccioná un servicio.',
            'invalid_choice': 'Seleccioná un servicio válido.'
        }
    )

    fecha = forms.DateField(
        label='Fecha preferida',
        widget=forms.DateInput(attrs={
            'type': 'date'
        }),
        error_messages={
            'required': 'Seleccioná una fecha.',
            'invalid': 'Ingresá una fecha válida.'
        }
    )

    horario = forms.ChoiceField(
        label='Horario',
        choices=HORARIOS,
        error_messages={
            'required': 'Seleccioná un horario.',
            'invalid_choice': 'Seleccioná un horario válido.'
        }
    )

    comentarios = forms.CharField(
        label='Comentarios',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Contanos si hay algo que debamos saber...',
            'rows': 4
        })
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()

        if len(nombre.split()) < 2:
            raise forms.ValidationError(
                'Ingresá tu nombre y apellido.'
            )

        if not all(parte.isalpha() for parte in nombre.split()):
            raise forms.ValidationError(
                'El nombre y apellido solo pueden contener letras.'
            )

        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()

        telefono_limpio = telefono.replace(' ', '').replace('-', '')

        if not telefono_limpio.isdigit():
            raise forms.ValidationError(
                'Ingresá un teléfono válido.'
            )

        if len(telefono_limpio) < 8:
            raise forms.ValidationError(
                'El teléfono debe tener al menos 8 números.'
            )

        return telefono

    def clean_patente(self):
        patente = self.cleaned_data.get('patente', '').strip().upper()

        if patente and not patente.isalnum():
            raise forms.ValidationError(
                'La patente solo puede contener letras y números.'
            )

        return patente

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')

        if fecha and fecha < date.today():
            raise forms.ValidationError(
                'La fecha del turno no puede ser anterior a hoy.'
            )

        return fecha

class TurnoPublicoForm(TurnoForm):
    vehiculo = None

    marca = forms.CharField(
        label='Marca',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: BMW'}),
        error_messages={'required': 'Ingresá la marca de tu vehículo.'},
    )
    modelo = forms.CharField(
        label='Modelo',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Serie 3'}),
        error_messages={'required': 'Ingresá el modelo de tu vehículo.'},
    )

    def clean(self):
        datos = super().clean()
        marca = datos.pop('marca', '')
        modelo = datos.pop('modelo', '')

        if marca and modelo:
            vehiculo = f'{marca} {modelo}'
            if len(vehiculo) > 100:
                self.add_error('modelo', 'La marca y el modelo juntos deben tener hasta 100 caracteres.')
            else:
                datos['vehiculo'] = vehiculo

        return datos


class SolicitudPanelForm(TurnoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].widget.format = '%Y-%m-%d'

    def clean_fecha(self):
        return self.cleaned_data['fecha']


class RegistroForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=150, error_messages={'required': 'Ingresá tu nombre.'})
    apellido = forms.CharField(label='Apellido', max_length=150, error_messages={'required': 'Ingresá tu apellido.'})
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=254,
        error_messages={'required': 'Ingresá tu correo electrónico.',
                        'invalid': 'Ingresá un correo electrónico válido.'},
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        error_messages={'required': 'Ingresá tu contraseña.'},
    )
    confirmar_password = forms.CharField(
        label='Repetir contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        error_messages={'required': 'Repetí tu contraseña.'},
    )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if not CorreoAutorizado.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Acceso restringido. No está autorizado a utilizar este sistema.')
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo electrónico.')

        return email

    def clean(self):
        datos = super().clean()
        if 'password' in datos and 'confirmar_password' in datos:
            if datos['password'] != datos['confirmar_password']:
                self.add_error('confirmar_password', 'Las contraseñas no coinciden.')
        if not all(campo in datos for campo in ('nombre', 'apellido', 'email', 'password')):
            return datos

        usuario = get_user_model()(first_name=datos['nombre'], last_name=datos['apellido'], email=datos['email'])
        try:
            validate_password(datos['password'], user=usuario)
        except forms.ValidationError as error:
            self.add_error('password', error)

        return datos

class ValidarCuentaForm(forms.Form):
    codigo = forms.RegexField(
        label='Código de validación',
        regex=r'\A[0-9]{6}\Z',
        max_length=6,
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'autocomplete': 'one-time-code'}),
        error_messages={
            'required': 'Ingresá el código de validación.',
            'invalid': 'Ingresá el código de seis dígitos que recibiste por correo.',
        },
    )

class IniciarSesionForm(AuthenticationForm):
    username = forms.EmailField(
        label='Correo electrónico',
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'username'}),
        error_messages={'required': 'Ingresá tu correo electrónico.',
                        'invalid': 'Ingresá un correo electrónico válido.'},
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
        error_messages={'required': 'Ingresá tu contraseña.'},
    )

    def clean(self):
        email = self.cleaned_data.get('username', '').strip().lower()
        password = self.cleaned_data.get('password')

        if email and password:
            username = sha256(email.encode()).hexdigest()
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    'Ingresá un correo y una contraseña válidos. La cuenta debe estar validada.'
                )
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data