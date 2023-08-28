import os
from git import Repo
from flask import request, jsonify, current_app
from paperfly import db
from paperfly.models import Repository
from paperfly.repo import bp
from paperfly.utils.paperfly_encryption import encrypt_content, decrypt_content

@bp.route('/clone', methods=['POST'])
def clone_repo():
    data = request.get_json()
    url = data.get('url')
    local_path = data.get('local_path')
    username = data.get('username', None)
    password = data.get('password', None)

    # Asegurarse de que la carpeta 'repos' exista y ajustar el local_path
    if not os.path.exists('repos'):
        os.makedirs(f'{current_app.config["BASE_WORKSPACE"]}/repos')
    full_local_path = os.path.join({current_app.config["BASE_WORKSPACE"]}, local_path)

    repo_record = Repository.query.filter_by(url=url).first()

    if not repo_record:
        encrypted_password = encrypt_content(password) if password else None
        new_repo = Repository(url=url, local_path=full_local_path, username=username, password=encrypted_password, cloned=False)
        db.session.add(new_repo)
        db.session.commit()
    else:
        if repo_record.cloned:
            return jsonify(message="Repositorio ya ha sido clonado."), 409

    if username and password:
        os.environ['GIT_USERNAME'] = username
        os.environ['GIT_PASSWORD'] = password

    try:
        Repo.clone_from(url, full_local_path)
        new_repo.cloned = True
        db.session.commit()
        return jsonify(message="Repositorio clonado con éxito."), 200
    except Exception as e:
        return jsonify(message=str(e)), 500

@bp.route('/pull/<int:repo_id>', methods=['GET'])
def pull_repo(repo_id):
    repo_record = Repository.query.get(repo_id)
    if not repo_record:
        return jsonify(message="Repositorio no encontrado."), 404

    if repo_record.username and repo_record.password:
        os.environ['GIT_USERNAME'] = repo_record.username
        os.environ['GIT_PASSWORD'] = decrypt_content(repo_record.password)

    try:
        repo = Repo(repo_record.local_path)
        origin = repo.remotes.origin
        origin.pull()
        return jsonify(message="Actualización del repositorio completada."), 200
    except Exception as e:
        return jsonify(message=str(e)), 500



@bp.route('/repositories', methods=['GET'])
def get_repositories():
    repos = Repository.query.all()
    repos_data = [{
        "id": repo.id,
        "url": repo.url,
        "local_path": repo.local_path,
        "username": repo.username,  # Por seguridad, considera no retornar esto en producción
        "cloned": repo.cloned,
        "created_at": repo.created_at.isoformat()
    } for repo in repos]
    return jsonify(repos_data), 200


@bp.route('/clone_or_pull', methods=['POST'])
def clone_or_pull_repo():
    data = request.get_json()
    url = data.get('url')
    default_local_path = url.rstrip('/').split('/')[-1].split('.')[0]
    local_path = data.get('local_path',default_local_path)
    username = data.get('username', None)
    password = data.get('password', None)
    branch = data.get('branch', 'master')  # Por defecto usará la rama master si no se proporciona

    # Asegurarse de que la carpeta 'repos' exista y ajustar el local_path f'{current_app.config["WORKSPACE"]}/repos
    if not os.path.exists('repos'):
        os.makedirs(os.path.join(current_app.config['BASE_WORKSPACE'],'repos'), exist_ok=True)
    full_local_path = os.path.join(current_app.config['BASE_WORKSPACE'], 'repos', local_path)

    repo_record = Repository.query.filter_by(url=url).first()

    if username and password:
        os.environ['GIT_USERNAME'] = username
        os.environ['GIT_PASSWORD'] = password

    # Si el repositorio no ha sido clonado previamente
    if not repo_record:
        try:
            Repo.clone_from(url, full_local_path, branch=branch)
            new_repo = Repository(url=url, local_path=full_local_path, username=username, password=password, cloned=True)
            db.session.add(new_repo)
            db.session.commit()
            return jsonify(message="Repositorio clonado con éxito."), 200
        except Exception as e:
            return jsonify(message=str(e)), 500
    else:  # Si el repositorio ya existe, hacemos un pull
        try:
            repo = Repo(repo_record.local_path)
            origin = repo.remotes.origin
            repo.git.checkout(branch)
            origin.pull(branch)
            return jsonify(message="Actualización del repositorio completada."), 200
        except Exception as e:
            return jsonify(message=str(e)), 500
