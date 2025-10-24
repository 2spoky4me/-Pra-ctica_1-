1) Guía de instalación y ejecución paso a paso

Este proyecto se puede ejecutar fácilmente mediante Docker Compose y el Makefile incluido.
Los pasos siguientes permiten levantar tanto el entorno de desarrollo como el de producción, verificar que funcionan correctamente y limpiarlos al finalizar.

Requisitos previos

Tener Docker Desktop (Windows/Mac) o Docker Engine + Docker Compose (Linux) instalado y en ejecución.

Todos los comandos deben ejecutarse desde la raíz del proyecto (Redes_prac1/).

Estructura del proyecto
Redes_prac1/
│
├── app/                     → Código de la aplicación Flask
│   ├── app.py               → Lógica principal
│   └── static/logo.png      → Imagen mostrada solo en producción
│
├── db/init/                 → Scripts SQL que inicializan la base de datos
│   └── 001_schema.sql
│
├── docker-compose.dev.yml   → Configuración del entorno de desarrollo
├── docker-compose.prod.yml  → Configuración del entorno de producción
├── .env.dev                 → Variables de entorno de desarrollo
├── .env.prod                → Variables de entorno de producción
├── Dockerfile               → Imagen base para el servicio Flask
└── Makefile                 → Simplifica el uso de Docker Compose

Entorno de desarrollo (DEV)

Levantar los contenedores:

make up-dev

Esto creará:

El contenedor web_dev (aplicación Flask)

El contenedor db_dev (PostgreSQL)

La red red_dev

El volumen vol_dev para mantener los datos persistentes

Comprobar que funciona:

http://localhost:8000/
 → mensaje de bienvenida

http://localhost:8000/status
 → estado de la base de datos

http://localhost:8000/form
 → formulario para añadir usuarios

http://localhost:8000/list
 → lista de usuarios guardados

Apagar el entorno:

make down-dev

Los datos añadidos se mantienen en el volumen vol_dev, incluso si se eliminan los contenedores.

Entorno de producción (PROD)

Levantar el entorno:

make up-prod

Esto creará:

El contenedor web_prod (Flask con caché e imagen estática)

El contenedor db_prod (PostgreSQL)

El contenedor cache (Redis)

La red red_prod

El volumen vol_prod para persistencia de datos

Comprobar funcionamiento:

http://localhost:8080/
 → mensaje de bienvenida

http://localhost:8080/form
 → formulario con imagen cacheada

http://localhost:8080/status
 → debe mostrar "db_connected": true, "cache_connected": true

http://localhost:8080/cache-test
 → incrementa el contador de visitas con Redis

Apagar el entorno:

make down-prod


El entorno de producción utiliza Redis para cachear datos y una imagen estática servida con cabeceras de caché, simulando un entorno real.

Limpiar todo

Para eliminar todos los contenedores, redes y volúmenes (de dev y prod):

make clean


Este comando borra también los volúmenes vol_dev y vol_prod, por lo que se perderán los datos almacenados en la base de datos.

2) Descripción de los entornos dev y prod

El proyecto está diseñado para funcionar en dos entornos claramente diferenciados: desarrollo (dev) y producción (prod).
Ambos entornos utilizan contenedores Docker, pero con configuraciones y objetivos distintos, lo que permite probar la aplicación en local antes de desplegarla en un entorno más realista.

2.1 Variables de entorno (.env)

Cada entorno (dev y prod) tiene su propio archivo .env con los valores necesarios para configurar los servicios.
Estas variables permiten definir de forma flexible el comportamiento de la aplicación sin modificar el código.

Variable	Entorno	Descripción	Motivo / Valor
APP_ENV	Ambos	Indica si la aplicación se ejecuta en modo dev o prod.	Flask usa esta variable para activar o desactivar características como la caché o la imagen estática.
WEB_PORT	Ambos	Puerto en el que Flask expone la aplicación.	En desarrollo es 8000 y en producción 8080, para evitar conflictos entre entornos.
DB_HOST	Ambos	Nombre del contenedor que actúa como servidor de base de datos.	Permite que Flask se conecte a la base de datos interna (db_dev o db_prod).
DB_NAME	Ambos	Nombre de la base de datos principal.	Se mantiene igual en ambos entornos para simplificar la configuración.
DB_USER	Ambos	Usuario de la base de datos PostgreSQL.	Necesario para autenticarse contra el servidor SQL.
DB_PASSWORD	Ambos	Contraseña asociada al usuario de la base de datos.	Se define solo en los .env, nunca en el código por seguridad.
DB_PORT	Ambos	Puerto estándar de PostgreSQL (5432).	Es el puerto oficial de PostgreSQL y el que escucha por defecto la imagen oficial.
REDIS_HOST	Solo prod	Nombre del contenedor Redis (cache).	Permite que Flask conecte con el servicio de caché solo en producción.
REDIS_PORT	Solo prod	Puerto estándar de Redis (6379).	Se mantiene el valor por defecto para compatibilidad con la imagen oficial de Redis.

2.2 Entorno de desarrollo (dev)

El entorno dev está pensado para programar, probar y depurar la aplicación de forma rápida.
Utiliza contenedores ligeros que permiten levantar la base de datos y la aplicación Flask con un solo comando (make up-dev).
Los datos de la base de datos se guardan en un volumen persistente llamado vol_dev, de modo que si se reinicia o elimina el contenedor, la información no se pierde.

En este entorno no hay caché de Redis ni archivos estáticos con almacenamiento en caché, lo que facilita ver los cambios de código o contenido al instante.
El contenedor principal se llama web_dev, la base de datos db_dev y se comunican mediante una red interna llamada red_dev.
De esta forma, todo el entorno de desarrollo queda aislado y no interfiere con el entorno de producción.

2.3 Entorno de producción (prod)

El entorno prod simula un despliegue real en un servidor.
Está optimizado para rendimiento y estabilidad, incluyendo un servicio adicional de caché Redis que mejora la eficiencia de la aplicación.
Los contenedores principales son web_prod (la aplicación Flask), db_prod (la base de datos PostgreSQL) y cache (el servicio Redis).
Todos ellos se comunican mediante una red interna privada llamada red_prod.

La base de datos en producción también utiliza un volumen persistente, llamado vol_prod, que garantiza que los datos se mantengan incluso si se eliminan o reinician los contenedores.
Además, en este entorno Flask sirve una pequeña imagen estática que se guarda en caché durante una hora en el navegador, lo que reduce las peticiones al servidor y demuestra el uso de caché en producción.

El entorno de producción se puede levantar con el comando make up-prod, y su puerto principal es el 8080, mientras que el entorno de desarrollo utiliza el 8000.

3) Diagrama de arquitectura del servicio


           ┌───────────────────────────┐
           │        Navegador          │
           │     (localhost:PUERTO)    │
           └─────────────┬─────────────┘
                         │
                  Peticiones HTTP
                         │
          ┌──────────────▼──────────────┐
          │         web_* (Flask)       │
          │  * web_dev  (puerto 8000)   │
          │  * web_prod (puerto 8080)   │
          └───────────┬───────┬────────┘
                      │       │
           (red_dev)  │       │  (red_prod)
                      │       │
        ┌─────────────▼───┐   │     ┌───────────────▼──────────────┐
        │   db_dev/db_prod │   │     │          cache (Redis)       │
        │  PostgreSQL      │   │     │    (solo en producción)      │
        └───────┬──────────┘   │     └──────────────┬───────────────┘
                │              │                    │
          vol_dev (dev)   vol_prod (prod)     Datos temporales en memoria
          Persistencia BD  Persistencia BD

Resumen por entorno:

Dev: web_dev + db_dev en red_dev, con volumen vol_dev. Sin Redis ni caché de navegador.

Prod: web_prod + db_prod + cache en red_prod, con volumen vol_prod. Imagen estática cacheada y endpoint de caché (/cache-test).

4) Resultados de las pruebas y verificaciones

Durante el desarrollo y despliegue del proyecto se realizaron diversas pruebas para garantizar el correcto funcionamiento de los contenedores, la base de datos, la caché y la persistencia de los datos. A continuación se resumen los resultados más relevantes.

Prueba 1: Arranque correcto de los servicios

Se ejecutó el comando make up-dev y make up-prod para levantar ambos entornos.
En ambos casos, los contenedores se iniciaron correctamente y mostraron el estado “healthy” al ejecutar:

docker compose --env-file .env.dev -f docker-compose.dev.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml ps


Resultado:
Los contenedores web_dev y db_dev en desarrollo funcionaron correctamente.
En producción, los contenedores web_prod, db_prod y cache también funcionaron correctamente.

Prueba 2: Persistencia de datos con volúmenes

Se añadió un registro mediante el formulario /form y posteriormente se detuvieron y eliminaron los contenedores con:

make down-dev
make down-prod


Luego se levantaron nuevamente con make up-dev y make up-prod.
Los registros previamente añadidos seguían presentes en la base de datos, lo que demuestra que los volúmenes (vol_dev y vol_prod) conservan los datos correctamente.

Resultado:
La base de datos mantiene los datos tras eliminar los contenedores.

Prueba 3: Endpoint de salud /status

El endpoint /status devuelve un JSON con el estado de conexión de los servicios:

{
  "db_connected": true,
  "cache_connected": true
}


Para comprobar el comportamiento dinámico, se detuvo el servicio de Redis en producción:

docker stop cache


Al recargar /status, el valor de "cache_connected" pasó a false, confirmando que el sistema detecta los fallos en tiempo real.

Resultado:
El healthcheck refleja correctamente el estado actual de los servicios dependientes.

Prueba 4: Caché en producción

En el entorno de producción, el formulario /form muestra una imagen (logo.png).
Esta imagen se almacena en caché durante una hora en el navegador.
Se verificó que, tras la primera carga, la siguiente solicitud obtiene un código HTTP 304 (Not Modified), lo que indica que el navegador la está sirviendo desde su caché sin volver a pedirla al servidor.

Resultado:
La caché estática del navegador funciona correctamente.

Prueba 5: Redis como sistema de caché

En el entorno de producción se ejecutó el endpoint /cache-test, que incrementa un contador almacenado en Redis:

{"ok": true, "visitas": 1}


Al repetir la petición, el contador aumentó (visitas: 2, visitas: 3, etc.), confirmando que los datos se mantienen temporalmente en memoria sin consultar la base de datos.

Resultado:
Redis funciona correctamente como sistema de caché temporal en producción.

Prueba 6: Reconstrucción completa

Se ejecutó make clean para eliminar contenedores, redes y volúmenes, y después se reconstruyeron ambos entornos desde cero con make rebuild-dev y make rebuild-prod.
El sistema se levantó sin errores, los esquemas SQL se cargaron automáticamente y los servicios quedaron disponibles.

Resultado:
El entorno puede reconstruirse completamente sin intervención manual.

Conclusión:
Todas las pruebas de conexión, persistencia, caché, healthcheck y reconstrucción fueron satisfactorias.
El sistema cumple con los objetivos de aislar los entornos, mantener persistencia de datos, reflejar el estado de los servicios y aprovechar mecanismos de caché en producción.

5) Explicación de los healthchecks

En esta práctica se han implementado varios healthchecks con el objetivo de supervisar el estado de los servicios que forman la aplicación (base de datos, backend Flask y caché Redis) y garantizar que el sistema detecte y gestione automáticamente posibles fallos.

Tipos de healthchecks utilizados

El proyecto implementa dos tipos de healthchecks complementarios:

Healthchecks de Docker → definidos en los archivos docker-compose.dev.yml y docker-compose.prod.yml, que son los que realmente utiliza Docker para marcar un contenedor como “healthy” o “unhealthy”.

Healthcheck interno de la aplicación Flask → mediante el endpoint /status, que devuelve el estado actual de la base de datos y de Redis.

5.1. Healthcheck del servicio PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME} -h localhost -p 5432"]
  interval: 5s
  timeout: 2s
  retries: 10


Qué hace:
Ejecuta el comando pg_isready, una herramienta nativa de PostgreSQL, que comprueba si el servidor está listo para aceptar conexiones.

Por qué se hace:

Garantiza que la base de datos esté completamente inicializada antes de que otros servicios (como Flask) intenten conectarse.

Si PostgreSQL tarda unos segundos en arrancar, este healthcheck evita errores de conexión prematuros.

Además, si la base de datos se detiene o deja de responder, Docker marcará el contenedor como unhealthy.

5.2. Healthcheck del servicio Flask
healthcheck:
  test:
    - CMD-SHELL
    - |
      python - << 'PY'
      import json, urllib.request, sys
      j = json.load(urllib.request.urlopen('http://localhost:8000/status'))
      sys.exit(0 if j.get('db_connected') else 1)
      PY
  interval: 10s
  timeout: 3s
  retries: 10


Qué hace:
Ejecuta un pequeño script en Python dentro del contenedor del servicio web que:

Llama al endpoint /status del propio servidor Flask.

Analiza la respuesta JSON.

Si el campo "db_connected" es true, el healthcheck pasa con éxito (código 0).
Si no, devuelve error (código 1) y Docker marca el contenedor como unhealthy.

Por qué se hace:

Permite comprobar no solo que el contenedor de Flask esté “encendido”, sino que realmente tenga conexión con la base de datos.

Detecta fallos en dependencias externas sin necesidad de reiniciar manualmente.

Es una validación más completa que simplemente revisar si el proceso de Flask sigue corriendo.

5.3. Healthcheck del servicio Redis (solo en producción)
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 3s
  retries: 5


Qué hace:
Usa el cliente oficial redis-cli para enviar el comando PING al servidor Redis.
Si la respuesta es PONG, el contenedor se considera saludable.

Por qué se hace:

Asegura que el servicio de caché esté disponible antes de que Flask intente usarlo.

Si Redis falla o se detiene, el healthcheck lo detecta automáticamente.

Evita tiempos de espera innecesarios en la aplicación cuando intenta conectar con Redis.

5.4. Endpoint /status dentro de Flask
@app.route("/status")
def status():
    db_ok = db_conn_ok()
    cache_ok = False
    if r:
        try:
            r.ping()
            cache_ok = True
        except Exception:
            cache_ok = False
    return jsonify({"db_connected": db_ok, "cache_connected": cache_ok})


Qué hace:
Devuelve un JSON que refleja el estado actual de los servicios dependientes:

db_connected: indica si la conexión a la base de datos PostgreSQL es correcta.

cache_connected: indica si Redis está disponible y responde al comando PING.

Por qué se hace:
Este endpoint permite comprobar el estado del sistema en tiempo real desde un navegador o herramienta externa.
También es el endpoint que el healthcheck de Docker usa internamente para evaluar el estado del contenedor.

6) Instrucciones de uso del Makefile o script (Makefile en mi caso)

| Comando             | Descripción rápida                                | Entorno |
| ------------------- | ------------------------------------------------- | ------- |
| `make up-dev`       | Levanta el entorno de desarrollo                  | Dev     |
| `make down-dev`     | Detiene el entorno de desarrollo                  | Dev     |
| `make rebuild-dev`  | Reconstruye imágenes en dev                       | Dev     |
| `make up-prod`      | Levanta el entorno de producción (con Redis)      | Prod    |
| `make down-prod`    | Detiene el entorno de producción                  | Prod    |
| `make rebuild-prod` | Reconstruye imágenes en prod                      | Prod    |
| `make ps`           | Muestra contenedores activos                      | Ambos   |
| `make logs`         | Muestra los registros (logs)                      | Ambos   |
| `make clean`        | Elimina todos los contenedores, redes y volúmenes | Ambos   |

