# Garage 27

Aplicación web desarrollada en Django para solicitar turnos y gestionar consultas de un taller ficticio de detailing automotor. Incluye autenticación de usuarios, un panel de solicitudes y una API REST. Los datos se guardan en PostgreSQL.

## Enlaces del proyecto

- [Repositorio en GitHub](https://github.com/hmarc953/Garage27)
- [Sitio desplegado en Render](https://garage27-ux9q.onrender.com/)

## Ejecución local

1. Clonar el repositorio y abrir la carpeta que contiene `manage.py`.
2. Crear y activar un entorno virtual de Python.
3. Instalar las dependencias:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Configurar la conexión a una base PostgreSQL local y las credenciales SMTP según los ajustes del proyecto.
5. Aplicar las migraciones e iniciar el servidor:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

6. Abrir [Garage 27 en local](http://127.0.0.1:8000/).

El envío de correos de confirmación de turnos y de validación de cuentas se prueba en local con SMTP, según la consigna.

## API REST

Los usuarios autorizados pueden consultar las solicitudes en formato JSON:

- `/api/consultas/` — Listado de solicitudes.
- `/api/consultas/<id>/` — Detalle de una solicitud.

## API externa

El formulario **Solicitar turno** utiliza vPIC de la NHTSA para sugerir marcas y los modelos de la marca elegida. Ambos campos también aceptan texto libre.

- [Documentación de vPIC](https://vpic.nhtsa.dot.gov/api/)
- [Endpoint utilizado](https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeId/0?format=json)