from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from hashlib import sha256
from secrets import randbelow
from smtplib import SMTPException
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError, transaction
from django.urls import reverse
from urllib.parse import urlencode
from django.core import signing

from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from rest_framework.response import Response

from urllib.request import urlopen

from django.core.cache import cache
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser

from .serializers import ModeloVehiculoSerializer, SolicitudTurnoSerializer
from .forms import SERVICIOS, RegistroForm, SolicitudPanelForm, TurnoPublicoForm, ValidarCuentaForm
from .models import CorreoAutorizado, SolicitudTurno, ValidacionCuenta

from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'mi_app/index.html')

def servicios(request):
    return render(request, 'mi_app/servicios.html')

def trabajos(request):
    return render(request, 'mi_app/trabajos.html')

def obtener_catalogo_vehiculos():
    clave_cache = 'vpic:catalogo-autos'
    catalogo = cache.get(clave_cache)

    if catalogo is not None:
        return catalogo

    url = 'https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeId/0?format=json'

    try:
        with urlopen(url, timeout=2) as respuesta:
            datos = JSONParser().parse(respuesta)

        serializer = ModeloVehiculoSerializer(data=datos['Results'], many=True)
        if serializer.is_valid():
            marcas_sugeridas = {
                'audi', 'bmw', 'chevrolet', 'citroen', 'dodge', 'fiat',
                'ford', 'honda', 'hyundai', 'jeep', 'kia', 'land rover',
                'mazda', 'mercedes-benz', 'mini', 'mitsubishi', 'nissan',
                'peugeot', 'porsche', 'ram', 'renault', 'subaru',
                'suzuki', 'toyota', 'volkswagen', 'volvo',
            }
            modelos_por_marca = {}

            for fila in serializer.validated_data:
                marca = fila['Make_Name']
                if marca.casefold() in marcas_sugeridas:
                    modelo = fila['Model_Name']
                    modelos_por_marca.setdefault(marca, set()).add(modelo)

            catalogo = {
                marca: sorted(modelos_por_marca[marca], key=str.casefold)
                for marca in sorted(modelos_por_marca, key=str.casefold)
            }

            if catalogo:
                cache.set(clave_cache, catalogo, timeout=24 * 60 * 60)
                return catalogo
    except (OSError, ParseError, KeyError, TypeError):
        pass

    cache.set(clave_cache, {}, timeout=5 * 60)
    return {}

@api_view(['GET'])
def catalogo_vehiculos_api(request):
    return Response(obtener_catalogo_vehiculos())

def turnos(request):
    if request.method == 'POST':
        form = TurnoPublicoForm(request.POST)

        if form.is_valid():
            datos = form.cleaned_data
            categoria = SolicitudTurno.clasificar_comentarios(datos['comentarios'])
            solicitud = SolicitudTurno.objects.create(**datos, categoria=categoria)
            if not settings.GARAGE27_ENVIO_EMAIL:
                messages.warning(
                    request,
                    'Recibimos tu solicitud. En esta versión no se envía '
                    'correo de confirmación. No hace falta que vuelvas a enviarla.'
                )
                return redirect('turnos')
            servicio = dict(form.fields['servicio'].choices).get(datos['servicio'])

            ############################
            # Mail para usuario
            ############################
            asunto = f'Garage 27 - Solicitud de turno recibida - {solicitud.get_categoria_display()}'

            mensaje_texto = f"""
            Garage 27

            Hola {datos['nombre']},

            Recibimos correctamente tu solicitud de turno.

            Vehículo: {datos['vehiculo']}
            Patente: {datos['patente'] or 'No informada'}
            Servicio: {servicio}
            Fecha preferida: {datos['fecha'].strftime('%d/%m/%Y')}
            Horario: {datos['horario']}

            Nos pondremos en contacto con vos para confirmar la disponibilidad del turno.

            Gracias por elegir Garage 27.
            """

            mensaje_html = f"""
            <!DOCTYPE html>

            <html>

            <body style="
                margin: 0;
                padding: 30px 15px;
                background-color: #111111;
                font-family: Arial, sans-serif;
                color: #F5F5F5;
            ">

                <div style="
                    max-width: 620px;
                    margin: 0 auto;
                    background-color: #2B2B2B;
                    border: 1px solid #3A3A3A;
                    overflow: hidden;
                ">

                    <!-- HEADER -->

                    <div style="
                        padding: 26px 30px;
                        background-color: #111111;
                    ">
                        <div style="
                            font-size: 25px;
                            font-weight: 700;
                            letter-spacing: 1px;
                            color: #F5F5F5;
                        ">
                            GARAGE <span style="color: #D62828;">27</span>
                        </div>
                    </div>


                    <!-- CONTENIDO -->

                    <div style="
                        padding: 32px 30px;
                    ">

                        <p style="
                            margin: 0 0 8px;
                            color: #D62828;
                            font-size: 12px;
                            font-weight: 700;
                            letter-spacing: 2px;
                        ">
                            SOLICITUD DE TURNO
                        </p>

                        <h2 style="
                            margin: 0 0 12px;
                            color: #F5F5F5;
                            font-size: 24px;
                        ">
                            ¡RECIBIMOS TU SOLICITUD!
                        </h2>

                        <p style="
                            margin: 0 0 28px;
                            color: #CCCCCC;
                            font-size: 15px;
                            line-height: 1.6;
                        ">
                            Hola {datos['nombre']}. Recibimos correctamente los datos
                            de tu solicitud. Nos pondremos en contacto con vos para
                            confirmar la disponibilidad del turno.
                        </p>


                        <!-- DETALLE -->

                        <div style="
                            padding: 22px;
                            background-color: #111111;
                            border-left: 3px solid #D62828;
                        ">

                            <div style="
                                margin-bottom: 18px;
                                color: #D62828;
                                font-size: 13px;
                                font-weight: 700;
                                letter-spacing: 1px;
                            ">
                                DETALLE DEL TURNO
                            </div>

                            <table style="
                                width: 100%;
                                border-collapse: collapse;
                                color: #F5F5F5;
                                font-size: 14px;
                            ">

                                <tr>
                                    <td style="padding: 8px 0; color: #999999;">
                                        Vehículo
                                    </td>
                                    <td style="padding: 8px 0; text-align: right;">
                                        {datos['vehiculo']}
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding: 8px 0; color: #999999;">
                                        Patente
                                    </td>
                                    <td style="padding: 8px 0; text-align: right;">
                                        {datos['patente'] or 'No informada'}
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding: 8px 0; color: #999999;">
                                        Servicio
                                    </td>
                                    <td style="padding: 8px 0; text-align: right;">
                                        {servicio}
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding: 8px 0; color: #999999;">
                                        Fecha preferida
                                    </td>
                                    <td style="padding: 8px 0; text-align: right;">
                                        {datos['fecha'].strftime('%d/%m/%Y')}
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding: 8px 0; color: #999999;">
                                        Horario
                                    </td>
                                    <td style="padding: 8px 0; text-align: right;">
                                        {datos['horario']}
                                    </td>
                                </tr>

                            </table>

                        </div>

                    </div>


                    <!-- FOOTER -->

                    <div style="
                        padding: 20px 30px;
                        background-color: #111111;
                        color: #888888;
                        font-size: 12px;
                        text-align: center;
                    ">
                        Detailing, estética y personalización de vehículos.<br>
                        © 2026 Garage 27
                    </div>

                </div>

            </body>

            </html>
            """

            email = EmailMultiAlternatives(
                subject=asunto,
                body=mensaje_texto,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[datos['email']]
            )

            email.attach_alternative(
                mensaje_html,
                "text/html"
            )

            ############################
            # Aviso al taller
            ############################
            mensaje_taller = '\n'.join([
                'Se recibió una nueva solicitud de turno en Garage 27.',
                '',
                f"Nombre y apellido: {datos['nombre']}",
                f"Correo electrónico: {datos['email']}",
                f"Teléfono: {datos['telefono']}",
                f"Vehículo: {datos['vehiculo']}",
                f"Patente: {datos['patente'] or 'No informada'}",
                f"Servicio: {servicio}",
                f"Fecha preferida: {datos['fecha']:%d/%m/%Y}",
                f"Horario: {datos['horario']}",
                f"Comentarios: {datos['comentarios'] or 'Sin comentarios'}",
            ])
            aviso_taller = EmailMultiAlternatives(
                subject=f'Garage 27 - Nueva solicitud de turno - {solicitud.get_categoria_display()}',
                body=mensaje_taller,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.GARAGE27_EMAIL_TALLER],
            )

            ############################
            # Mandar mails
            ############################
            try:
                confirmacion_enviada = email.send(fail_silently=False) == 1
            except (SMTPException, OSError):
                confirmacion_enviada = False

            try:
                aviso_taller.send(fail_silently=False)
            except (SMTPException, OSError):
                logger.exception('No se pudo enviar el aviso al taller.')

            if confirmacion_enviada:
                messages.success(request, 'Tu solicitud de turno fue recibida correctamente.')
            else:
                messages.warning(
                    request,
                    'Recibimos tu solicitud, pero no pudimos enviarte el correo de '
                    'confirmación. No hace falta que vuelvas a enviarla.'
                )

            return redirect('turnos')

    else:
        form = TurnoPublicoForm()

    return render(request, 'mi_app/turnos.html', {
        'form': form,
    })

def registro(request):
    form = RegistroForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and form.is_valid():
        if not settings.GARAGE27_ENVIO_EMAIL:
            form.add_error(
                None,
                'El registro por correo se prueba en el entorno local. '
                'Si ya tenés una cuenta validada, podés iniciar sesión.'
            )
            return render(request, 'mi_app/registro.html', {'form': form})
        datos = form.cleaned_data
        email = datos['email']
        codigo = f'{randbelow(1_000_000):06d}'

        try:
            with transaction.atomic():
                usuario = get_user_model().objects.create_user(
                    username=sha256(email.encode()).hexdigest(),
                    email=email,
                    first_name=datos['nombre'],
                    last_name=datos['apellido'],
                    password=datos['password'],
                    is_active=False,
                )
                ValidacionCuenta.objects.create(usuario=usuario, codigo_hash=make_password(codigo))
                token = signing.dumps(usuario.pk, salt='garage27.validar_cuenta')
                ruta = reverse('validar_cuenta')
                enlace = request.build_absolute_uri(f"{ruta}?{urlencode({'token': token})}")
                aviso = EmailMultiAlternatives(
                    subject='Garage 27 - Validá tu cuenta',
                    body=f"Hola, {datos['nombre']}.\n\nTu código de validación es {codigo}.\n"
                         f'Ingresá el código en este enlace:\n{enlace}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )
                aviso.send()
        except IntegrityError:
            form.add_error('email', 'Ya existe una cuenta con este correo electrónico.')
        except (SMTPException, OSError):
            form.add_error(None, 'No pudimos enviar el correo de validación. Intentá de nuevo.')
        else:
            request.session['validacion_usuario_id'] = usuario.pk
            messages.success(request, 'Le llegará un correo para validar su cuenta')
            return redirect('validar_cuenta')

    return render(request, 'mi_app/registro.html', {'form': form})


def validar_cuenta(request):
    token = request.GET.get('token')
    if request.method == 'GET' and token:
        try:
            usuario_id = signing.loads(token, salt='garage27.validar_cuenta', max_age=24 * 60 * 60)
        except signing.BadSignature:
            messages.error(request, 'El enlace de validación es inválido o venció.')
        else:
            request.session['validacion_usuario_id'] = usuario_id
        return redirect('validar_cuenta')

    usuario_id = request.session.get('validacion_usuario_id')

    if usuario_id is not None and get_user_model().objects.filter(pk=usuario_id, is_active=True).exists():
        request.session.pop('validacion_usuario_id', None)
        return render(request, 'mi_app/registro.html', {
            'validacion_pendiente': True,
            'cuenta_ya_validada': True,
        })

    form = ValidarCuentaForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and form.is_valid():
        codigo = form.cleaned_data['codigo']

        with transaction.atomic():
            validacion = ValidacionCuenta.objects.select_for_update().filter(
                usuario_id=usuario_id,
                usuario__is_active=False,
            ).first()

            if validacion is None or validacion.intentos >= 5:
                form.add_error('codigo', 'El código no está disponible o se agotaron los intentos.')
            elif timezone.now() >= validacion.creado_en + timedelta(hours=24):
                form.add_error('codigo', 'El código de validación venció.')
            elif not check_password(codigo, validacion.codigo_hash):
                validacion.intentos += 1
                validacion.save(update_fields=['intentos'])
                form.add_error('codigo', 'El código ingresado es incorrecto.')
            else:
                usuario = validacion.usuario
                usuario.is_active = True
                usuario.is_staff = True
                usuario.save(update_fields=['is_active', 'is_staff'])
                validacion.delete()
                request.session.pop('validacion_usuario_id', None)
                return render(request, 'mi_app/registro.html', {
                    'validacion_pendiente': True,
                    'cuenta_ya_validada': True,
                    'validacion_exitosa': True,
                })

    return render(request, 'mi_app/registro.html', {
        'form': form,
        'validacion_pendiente': True,
        'mostrar_codigo': usuario_id is not None,
    })

def puede_acceder_al_panel(usuario):
    if not usuario.is_authenticated:
        return False

    if not usuario.is_active or not CorreoAutorizado.objects.filter(email__iexact=usuario.email).exists():
        raise PermissionDenied

    return True


@user_passes_test(puede_acceder_al_panel)
def panel_solicitudes(request):
    solicitudes = list(SolicitudTurno.objects.order_by('-pk'))
    resumen = dict.fromkeys(SolicitudTurno.Categoria.values, 0)
    servicios = dict(SERVICIOS)

    for solicitud in solicitudes:
        resumen[solicitud.categoria] += 1
        solicitud.servicio_nombre = servicios.get(solicitud.servicio, solicitud.servicio)

    return render(request, 'mi_app/panel.html', {
        'solicitudes': solicitudes,
        'total': len(solicitudes),
        'resumen': [
            (etiqueta, resumen[categoria])
            for categoria, etiqueta in SolicitudTurno.Categoria.choices
        ],
    })


@user_passes_test(puede_acceder_al_panel)
def guardar_solicitud_panel(request, pk=None):
    solicitud = get_object_or_404(SolicitudTurno, pk=pk) if pk is not None else None
    campos = SolicitudPanelForm.base_fields
    datos_iniciales = {campo: getattr(solicitud, campo) for campo in campos} if solicitud else None

    form = SolicitudPanelForm(
        request.POST if request.method == 'POST' else None,
        initial=datos_iniciales,
    )

    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        categoria = SolicitudTurno.clasificar_comentarios(datos['comentarios'])

        if solicitud is None:
            SolicitudTurno.objects.create(**datos, categoria=categoria)
            messages.success(request, 'La solicitud fue creada.')
        else:
            for campo, valor in datos.items():
                setattr(solicitud, campo, valor)

            solicitud.categoria = categoria
            solicitud.save(update_fields=[*datos, 'categoria'])
            messages.success(request, 'La solicitud fue actualizada.')

        return redirect('panel_solicitudes')

    return render(request, 'mi_app/panel_formulario.html', {
        'form': form,
        'titulo': 'Editar solicitud' if solicitud else 'Nueva solicitud',
    })


@user_passes_test(puede_acceder_al_panel)
@require_POST
def eliminar_solicitud_panel(request, pk):
    solicitud = get_object_or_404(SolicitudTurno, pk=pk)
    solicitud.delete()
    messages.success(request, 'La solicitud fue eliminada.')
    return redirect('panel_solicitudes')


class PermisoConsultas(BasePermission):
    def has_permission(self, request, view):
        return puede_acceder_al_panel(request.user)


class ConsultasAPI(ListAPIView):
    queryset = SolicitudTurno.objects.order_by('-pk')
    serializer_class = SolicitudTurnoSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [PermisoConsultas]
    renderer_classes = [JSONRenderer]

class ConsultaDetalleAPI(RetrieveAPIView):
    queryset = SolicitudTurno.objects.all()
    serializer_class = SolicitudTurnoSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [PermisoConsultas]
    renderer_classes = [JSONRenderer]