from app import create_app, db
import logging

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)