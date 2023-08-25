#!/bin/sh

# Verifica si este es el proceso de inicialización
if [ "$INIT_PROCESS" = "true" ]; then
    # Realiza las migraciones de la base de datos si aún no se han hecho
    if [ ! -f /app/.db_initialized ]; then
        echo "Initializing database migrations..."
        flask db init
        flask db migrate
        flask db upgrade
        touch /app/.db_initialized
    fi
fi

# Ejecuta el servidor Gunicorn con los parámetros proporcionados
gunicorn 'app:create_app()' -b 0.0.0.0:5000 --workers 3 --log-level info