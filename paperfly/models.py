from datetime import datetime
from paperfly import db

class NotebookJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_notebook = db.Column(db.String, nullable=False)
    output_notebook = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default="pending", nullable=False)  # "pending", "running", "completed", "failed"
    message = db.Column(db.String)  # Para almacenar mensajes de error o información adicional
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, unique=True, nullable=False)
    local_path = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, nullable=True)  # Puedes encriptar esto por seguridad adicional
    password = db.Column(db.String, nullable=True)  # Puedes encriptar esto por seguridad adicional
    cloned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
