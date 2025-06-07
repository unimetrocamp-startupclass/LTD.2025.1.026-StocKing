# app.py
import os
from flask import Flask
from db import db
from routes import main as main_blueprint

def create_app():
    """
    Função que cria e configura a aplicação Flask (Application Factory).
    """
    app = Flask(__name__)

    # --- CONFIGURAÇÃO ---
    app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura-e-dificil-de-adivinhar'
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'estoque.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- INICIALIZAÇÃO DE EXTENSÕES ---
    db.init_app(app)

    # --- REGISTRO DE BLUEPRINTS ---
    app.register_blueprint(main_blueprint)

    # --- CRIAR BANCO DE DADOS ---
    with app.app_context():
        # --- LINHAS ADICIONADAS PARA CORRIGIR O ERRO ---
        # Garante que a pasta 'instance' exista antes de criar o DB
        instance_path = os.path.join(basedir, 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        # -------------------------------------------------
        
        db.create_all()

    return app

# --- EXECUÇÃO ---
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)