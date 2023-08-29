from paperfly import db
from paperfly.models import NotebookJob
from paperfly.notebook_execution import bp
import papermill as pm
from flask import request, jsonify, current_app
from paperfly.utils.auth import require_token
from nbconvert import HTMLExporter
import json
import os

@bp.route('/execute-notebook', methods=['POST'])
@require_token
def execute_notebook():
    data = request.get_json()
    input_notebook = os.path.join(current_app.config['BASE_WORKSPACE'],data.get('input_notebook'))

    
    parameters = data.get('parameters', {})

    if not input_notebook:
        return jsonify(message="input_notebook y output_notebook son obligatorios."), 400

    job = NotebookJob(input_notebook=input_notebook, output_notebook="", status="pending")
    db.session.add(job)
    db.session.commit()


    output_notebook_base =os.path.join(current_app.config['BASE_WORKSPACE'],'jobs', str(job.id) )
    os.makedirs(output_notebook_base, exist_ok=True)

    output_notebook = os.path.join(output_notebook_base,'output.ipynb')

    try:
        job.status = "running"
        db.session.commit()

        pm.execute_notebook(
            input_notebook,
            output_notebook,
            parameters=parameters
        )

        # Convertir el output_notebook a HTML
        html_exporter = HTMLExporter()
        (body, resources) = html_exporter.from_filename(output_notebook)

        # Guardar el archivo HTML en el mismo directorio que output_notebook
        html_output_path = os.path.join(output_notebook_base,'output.html')
        with open(html_output_path, 'w') as html_file:
            html_file.write(body)

                # Leer el archivo .ipynb como un JSON
        with open(output_notebook, 'r') as f:
            notebook_data = json.load(f)

        job.status = "completed"
        db.session.commit()

        return jsonify(message="Notebook ejecutado con éxito.", output=notebook_data), 200

    except Exception as e:
        job.status = "failed"
        job.message = str(e)
        db.session.commit()
        current_app.logger.exception("Error Notebook Execution")

        with open(output_notebook, 'r') as f:
            notebook_data = json.load(f)
        return jsonify(message=str(e), output=notebook_data), 500

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