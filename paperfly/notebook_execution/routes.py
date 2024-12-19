import os
import json
from flask import Blueprint, request, jsonify, current_app, url_for
from nbconvert import HTMLExporter
from papermill import execute_notebook
from .models import db, NotebookJob  # Suponiendo que tu modelo está definido aquí
from .decorators import require_token  # Decorador para manejar tokens

bp = Blueprint('notebook_execution', __name__)

@bp.route('/execute-notebook', methods=['POST'])
@require_token
def execute_notebook():
    data = request.get_json()
    input_notebook = os.path.join(current_app.config['BASE_WORKSPACE'], data.get('input_notebook'))
    parameters = data.get('parameters', {})

    # Validar que los parámetros sean un diccionario
    if not isinstance(parameters, dict):
        return jsonify(message="Los parámetros deben ser un diccionario válido."), 400

    if not input_notebook or not os.path.isfile(input_notebook):
        return jsonify(message="El campo 'input_notebook' es obligatorio y debe ser un archivo válido."), 400

    job = NotebookJob(input_notebook=input_notebook, output_notebook="", status="pending")
    db.session.add(job)
    db.session.commit()

    output_notebook_base = os.path.join(current_app.config['BASE_WORKSPACE'], 'jobs', str(job.id))
    os.makedirs(output_notebook_base, exist_ok=True)
    output_notebook = os.path.join(output_notebook_base, 'output.ipynb')

    try:
        job.status = "running"
        db.session.commit()

        # Cambiar el directorio de trabajo al directorio del notebook
        notebook_dir = os.path.dirname(input_notebook)
        os.chdir(notebook_dir)

        # Ejecutar el notebook
        execute_notebook(
            input_path=input_notebook,
            output_path=output_notebook,
            parameters=parameters
        )

        # Convertir el output_notebook a HTML
        html_exporter = HTMLExporter()
        (body, resources) = html_exporter.from_filename(output_notebook)

        html_output_path = os.path.join(output_notebook_base, 'output.html')
        with open(html_output_path, 'w') as html_file:
            html_file.write(body)

        with open(output_notebook, 'r') as f:
            notebook_data = json.load(f)

        job.status = "completed"
        db.session.commit()

        html_url = url_for('notebook_execution.get_job_html', job_id=job.id, _external=True)

        return jsonify(
            message="Notebook ejecutado con éxito.",
            output_url=html_url,
            output_notebook=notebook_data
        ), 200

    except Exception as e:
        job.status = "failed"
        job.message = str(e)
        db.session.commit()
        current_app.logger.exception("Error ejecutando notebook")

        return jsonify(message=str(e)), 500

@bp.route('/jobs', methods=['GET'])
@require_token
def get_jobs():
    jobs = NotebookJob.query.all()
    jobs_data = [{
        "id": job.id,
        "input_notebook": job.input_notebook,
        "output_notebook": job.output_notebook,
        "status": job.status,
        "message": job.message,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat()
    } for job in jobs]
    return jsonify(jobs_data), 200

@bp.route('/job/<int:job_id>/html', methods=['GET'])
def get_job_html(job_id):
    """
    Devuelve el archivo HTML generado para un job específico por ID.
    """
    # Comprobar si el job existe
    job = NotebookJob.query.get_or_404(job_id)

    # Asegúrate de que el job se haya completado con éxito
    if job.status != "completed":
        return jsonify(message="El job no se ha completado con éxito."), 400

    # Definir la ruta del archivo HTML
    html_output_path = os.path.join(current_app.config['BASE_WORKSPACE'], 'jobs', str(job.id), 'output.html')

    # Comprobar si el archivo HTML existe
    if not os.path.exists(html_output_path):
        return jsonify(message="El archivo HTML no se encontró."), 404

    # Devolver el archivo HTML
    return send_from_directory(os.path.dirname(html_output_path), 'output.html'), 200
