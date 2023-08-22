from datetime import datetime
from app import db

class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"APIKey('{self.key}', '{self.created_at}')"

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
