from flask_restful import Resource
from app.main import bp

class MainResource(Resource):
    def get(self):
        return {'message': 'Bienvenido a la API'}