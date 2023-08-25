#!/bin/sh

# Ejecuta el servidor Gunicorn con los parámetros proporcionados
gunicorn 'app:create_app()' -b 0.0.0.0:5000 --workers 3 --log-level info