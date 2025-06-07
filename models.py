# models.py
from db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    has_permission = db.Column(db.Boolean, default=False, nullable=False)
    
    # --- RELACIONAMENTO ADICIONADO ---
    # Isso cria uma lista de produtos cadastrados por este usuário.
    products = db.relationship('Product', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    tipo_servico = db.Column(db.String(100), nullable=False)
    data_recebimento = db.Column(db.Date, nullable=False)
    data_envio_previsto = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    
    # --- NOVO CAMPO ADICIONADO ---
    # Armazena o ID do usuário que cadastrou o produto.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)