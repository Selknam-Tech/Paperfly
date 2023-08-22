from app import db
from app.models import NotebookJob
from app.notebook_execution import bp
import papermill as pm
from flask import request, jsonify
from app.utils.auth import require_token

@bp.route('/execute-notebook', methods=['POST'])
@require_token
def execute_notebook():
    data = request.get_json()
    input_notebook = data.get('input_notebook')
    output_notebook = data.get('output_notebook')
    parameters = data.get('parameters', {})

    if not input_notebook or not output_notebook:
        return jsonify(message="input_notebook y output_notebook son obligatorios."), 400

    job = NotebookJob(input_notebook=input_notebook, output_notebook=output_notebook, status="pending")
    db.session.add(job)
    db.session.commit()

    try:
        job.status = "running"
        db.session.commit()

        pm.execute_notebook(
            input_notebook,
            output_notebook,
            parameters=parameters
        )

        job.status = "completed"
        db.session.commit()

        return jsonify(message="Notebook ejecutado con éxito."), 200

    except Exception as e:
        job.status = "failed"
        job.message = str(e)
        db.session.commit()
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