import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from datetime import datetime
from db import db
from models import User, Product
from analysis_generator import generate_reports

main = Blueprint('main', __name__)

def permission_required(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça o login para acessar esta página.', 'warning')
            return redirect(url_for('main.login'))
        user = User.query.get(session['user_id'])
        if not user or not user.has_permission:
            return redirect(url_for('main.no_permission'))
        return f(*args, **kwargs)
    return wrap

# --- ROTAS DE AUTENTICAÇÃO ---
@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and user.check_password(request.form.get('senha')):
            session['user_id'] = user.id
            session['user_name'] = user.nome
            if user.has_permission:
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                return redirect(url_for('main.no_permission'))
        else:
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('main.login'))
    return render_template('login.html')

@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        if request.form.get('senha') != request.form.get('confirmar_senha'):
            flash('As senhas não coincidem!', 'danger')
            return redirect(url_for('main.cadastro'))
        if User.query.filter_by(email=request.form.get('email')).first():
            flash('Este email já está cadastrado.', 'warning')
            return redirect(url_for('main.cadastro'))
        new_user = User(
            nome=request.form.get('nome'),
            email=request.form.get('email'),
            has_permission=request.form.get('permission') == 'on'
        )
        new_user.set_password(request.form.get('senha'))
        db.session.add(new_user)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça o login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('cadastro.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.login'))

@main.route('/no-permission')
def no_permission():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('no_permission.html')

# --- ROTAS DE PRODUTOS (CRUD) ---
@main.route('/dashboard')
@permission_required
def dashboard():
    search_query = request.args.get('q', '')
    if search_query:
        search_term = f"%{search_query}%"
        products = Product.query.filter(
            Product.nome.ilike(search_term) |
            Product.codigo.ilike(search_term) |
            Product.description.ilike(search_term)
        ).order_by(Product.id.desc()).all()
    else:
        products = Product.query.order_by(Product.id.desc()).all()
    return render_template('index.html', products=products)

@main.route('/add_product', methods=['POST'])
@permission_required
def add_product():
    try:
        novo_produto = Product(
            nome=request.form['nome'],
            codigo=request.form['codigo'],
            quantidade=int(request.form['quantidade']),
            tipo_servico=request.form.get('tipo_servico'),
            data_recebimento=datetime.strptime(request.form['data_recebimento'], '%Y-%m-%d').date(),
            data_envio_previsto=datetime.strptime(request.form['data_envio_previsto'], '%Y-%m-%d').date(),
            description=request.form.get('description', ''),
            user_id=session['user_id']
        )
        db.session.add(novo_produto)
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar produto: {e}', 'danger')
    return redirect(url_for('main.dashboard'))

@main.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@permission_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        try:
            product.nome = request.form['nome']
            product.codigo = request.form['codigo']
            product.quantidade = int(request.form['quantidade'])
            product.tipo_servico = request.form.get('tipo_servico')
            product.data_recebimento = datetime.strptime(request.form['data_recebimento'], '%Y-%m-%d').date()
            product.data_envio_previsto = datetime.strptime(request.form['data_envio_previsto'], '%Y-%m-%d').date()
            product.description = request.form.get('description', '')
            db.session.commit()
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar produto: {e}', 'danger')
    return render_template('edit.html', product=product)

@main.route('/delete_product/<int:id>', methods=['POST'])
@permission_required
def delete_product(id):
    product_to_delete = Product.query.get_or_404(id)
    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        flash('Produto deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar produto: {e}', 'danger')
    return redirect(url_for('main.dashboard'))

# --- ROTA PARA GERAR E BAIXAR RELATÓRIO ---
@main.route('/gerar-relatorio')
@permission_required
def gerar_relatorio():
    flash('Seu relatório está sendo gerado. O download começará em breve.', 'info')
    
    # Chama nossa função que gera os relatórios e pega o caminho do CSV
    path_do_csv = generate_reports()
    
    if path_do_csv:
        try:
            # Envia o arquivo para o usuário como um anexo para download
            return send_file(path_do_csv, as_attachment=True)
        except Exception as e:
            flash(f"Erro ao tentar enviar o arquivo: {e}", "danger")
            return redirect(url_for('main.dashboard'))
    else:
        # Caso não haja dados para gerar o relatório
        flash('Não há produtos cadastrados para gerar um relatório.', 'warning')
        return redirect(url_for('main.dashboard'))