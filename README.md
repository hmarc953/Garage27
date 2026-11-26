# Garage 27

Aplicación web desarrollada en Django para solicitar turnos y gestionar consultas de un taller ficticio de detailing automotor. Incluye autenticación de usuarios, un panel de solicitudes y una API REST. Los datos se guardan en PostgreSQL.

## Enlaces del proyecto

- [Repositorio en GitHub](https://github.com/hmarc953/Garage27)
- [Sitio desplegado en Render](https://garage27-ux9q.onrender.com/)

---

## Ejecución local

### 1. Abrir el proyecto en PyCharm 

1. Clonar el repositorio o extraer el zip 
2. En PyCharm, ir a **File → Open** y seleccionar la carpeta `garage27` que contiene `manage.py`.

### 2. Instalar las dependencias

3. Abrir `manage.py` y hacer clic en **Create a virtual environment using requirements.txt**.
4. Elegir **Python 3.14** y confirmar. PyCharm creará el entorno virtual e instalará las dependencias del proyecto.

### 3. Configurar la base de datos local

5. Con PostgreSQL en ejecución, abrir pgAdmin y crear una base de datos vacía.
6. Abrir el archivo `.env` incluido en el ZIP, ubicado junto a `manage.py`.
7. Ajustar `DATABASE_URL` con el usuario, la contraseña, el puerto y el nombre de la base local. Por ejemplo:
 
    ```dotenv
   DATABASE_URL=postgresql://USUARIO:CONTRASENA@localhost:5432/garage27
   ```

### 4. Aplicar las migraciones e iniciar Django

8. Aplicar las migraciones e iniciar el servidor:

   ```
   python manage.py migrate
   python manage.py runserver
   ```

9. Abrir [Garage 27 en local](http://127.0.0.1:8000/).

El envío de correos de confirmación de turnos y de validación de cuentas se prueba en local con SMTP, según la consigna.

---

## API REST

Los usuarios autorizados pueden consultar las solicitudes en formato JSON:

- `/api/consultas/` — Listado de solicitudes.
- `/api/consultas/<id>/` — Detalle de una solicitud.

## API externa

El formulario **Solicitar turno** utiliza vPIC de la NHTSA para sugerir marcas y los modelos de la marca elegida. Ambos campos también aceptan texto libre.

- [Documentación de vPIC](https://vpic.nhtsa.dot.gov/api/)
- [Endpoint utilizado](https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeId/0?format=json)