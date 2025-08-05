# app.py
import sqlite3
import math
import os
from flask import Flask, render_template, request, redirect, url_for, g, flash, send_from_directory
from datetime import date, datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')

app = Flask(__name__)
DATABASE = 'alugueis.db'
app.secret_key = 'sua_chave_secreta_super_segura_aqui'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user_data = db.execute('SELECT id, username FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    if user_data:
        return User(id=user_data['id'], username=user_data['username'])
    return None

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        db = get_db()
        user_data = db.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        if user_data and check_password_hash(user_data['password'], password):
            user = User(id=user_data['id'], username=user_data['username'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Utilizador ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        db = get_db()
        user_existente = db.execute('SELECT id FROM usuarios WHERE username = ?', (username,)).fetchone()
        if user_existente:
            flash('Este nome de utilizador já existe. Por favor, escolha outro.', 'danger')
            return redirect(url_for('registrar'))
        
        hashed_password = generate_password_hash(password)
        db.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (username, hashed_password))
        db.commit()
        flash('Conta criada com sucesso! Por favor, faça login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('registrar.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'success')
    return redirect(url_for('login'))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    db = get_db()
    if request.method == 'POST':
        novo_username, senha_atual = request.form['username'], request.form['current_password']
        nova_senha, confirmar_senha = request.form['new_password'], request.form['confirm_password']
        user_data = db.execute('SELECT * FROM usuarios WHERE id = ?', (current_user.id,)).fetchone()
        if not check_password_hash(user_data['password'], senha_atual):
            flash('Senha atual incorreta. As alterações não foram salvas.', 'danger')
            return redirect(url_for('perfil'))
        if novo_username != user_data['username']:
            user_existente = db.execute('SELECT id FROM usuarios WHERE username = ?', (novo_username,)).fetchone()
            if user_existente:
                flash('Este nome de utilizador já está em uso. Por favor, escolha outro.', 'danger')
                return redirect(url_for('perfil'))
            db.execute('UPDATE usuarios SET username = ? WHERE id = ?', (novo_username, current_user.id))
            flash('Nome de utilizador atualizado com sucesso!', 'success')
        if nova_senha:
            if nova_senha != confirmar_senha:
                flash('As novas senhas não coincidem.', 'danger')
                return redirect(url_for('perfil'))
            hashed_password = generate_password_hash(nova_senha)
            db.execute('UPDATE usuarios SET password = ? WHERE id = ?', (hashed_password, current_user.id))
            flash('Senha atualizada com sucesso!', 'success')
        db.commit()
        return redirect(url_for('perfil'))
    user_data = db.execute('SELECT username FROM usuarios WHERE id = ?', (current_user.id,)).fetchone()
    return render_template('perfil.html', user=user_data)

@app.route('/')
@login_required
def index():
    db = get_db()
    termo_busca = request.args.get('busca', '')
    query_sql = """
    SELECT a.id, a.data_vencimento, a.pago, a.valor_aluguel, c.apelido as apelido_casa, i.nome as nome_inquilino, d.nome_original as nome_documento, d.nome_seguro as caminho_documento
    FROM alugueis a JOIN casas c ON a.casa_id = c.id LEFT JOIN inquilinos i ON a.inquilino_id = i.id LEFT JOIN documentos d ON d.aluguel_id = a.id
    WHERE c.usuario_id = ?"""
    params = [current_user.id]
    if termo_busca:
        query_sql += " AND (LOWER(COALESCE(i.nome, '')) LIKE ? OR LOWER(c.endereco) LIKE ? OR LOWER(c.apelido) LIKE ?)"
        search_term = f"%{termo_busca.lower()}%"
        params.extend([search_term, search_term, search_term])
    query_sql += " ORDER BY a.data_vencimento DESC"
    alugueis = db.execute(query_sql, params).fetchall()
    hoje = date.today()
    pendentes_processados = []
    for aluguel in alugueis:
        aluguel_dict = dict(aluguel)
        vencimento_dt = datetime.strptime(aluguel_dict['data_vencimento'], '%Y-%m-%d').date()
        aluguel_dict['vencimento_br'] = vencimento_dt.strftime('%d/%m/%Y')
        if aluguel_dict['pago'] == 0:
            aluguel_dict['vencido'] = vencimento_dt < hoje
            pendentes_processados.append(aluguel_dict)
    pagos = [dict(aluguel) for aluguel in alugueis if aluguel['pago'] == 1]
    for aluguel_pago in pagos:
        vencimento_dt = datetime.strptime(aluguel_pago['data_vencimento'], '%Y-%m-%d').date()
        aluguel_pago['vencimento_br'] = vencimento_dt.strftime('%d/%m/%Y')
    total_pendente = sum(p['valor_aluguel'] for p in pendentes_processados if p['valor_aluguel'] is not None)
    mes_atual_str = hoje.strftime('%Y-%m')
    total_recebido_mes_row = db.execute("SELECT SUM(a.valor_aluguel) as total FROM alugueis a JOIN casas c ON a.casa_id = c.id WHERE a.pago = 1 AND strftime('%Y-%m', a.data_vencimento) = ? AND c.usuario_id = ?", (mes_atual_str, current_user.id)).fetchone()
    total_recebido_mes = total_recebido_mes_row['total'] or 0
    nome_mes_atual = hoje.strftime('%B de %Y').capitalize()
    return render_template('index.html', pendentes=pendentes_processados, pagos=pagos, termo_busca=termo_busca, total_pendente=total_pendente, total_recebido_mes=total_recebido_mes, nome_mes_atual=nome_mes_atual)

@app.route('/uploads/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    
@app.route('/alugueis/pendentes')
@login_required
def listar_pendentes():
    db = get_db()
    hoje = date.today()
    query = "SELECT a.data_vencimento, c.apelido as apelido_casa, i.nome as nome_inquilino FROM alugueis a JOIN casas c ON a.casa_id = c.id LEFT JOIN inquilinos i ON a.inquilino_id = i.id WHERE a.pago = 0 AND c.usuario_id = ?"
    alugueis_pendentes = db.execute(query, (current_user.id,)).fetchall()
    atrasados, prestes_a_vencer = [], []
    for aluguel_row in alugueis_pendentes:
        aluguel = dict(aluguel_row)
        data_vencimento = datetime.strptime(aluguel['data_vencimento'], '%Y-%m-%d').date()
        diferenca_dias = (data_vencimento - hoje).days
        aluguel['data_vencimento_str'] = data_vencimento.strftime('%d/%m/%Y')
        aluguel['diferenca_dias'] = diferenca_dias
        if diferenca_dias < 0: atrasados.append(aluguel)
        elif 0 <= diferenca_dias <= 5: prestes_a_vencer.append(aluguel)
    return render_template('pendentes.html', atrasados=atrasados, prestes_a_vencer=prestes_a_vencer)

@app.route('/casas')
@login_required
def listar_casas():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    ITENS_POR_PAGINA = 10
    offset = (page - 1) * ITENS_POR_PAGINA
    total_casas = db.execute('SELECT COUNT(id) FROM casas WHERE usuario_id = ?', (current_user.id,)).fetchone()[0]
    total_paginas = math.ceil(total_casas / ITENS_POR_PAGINA)
    casas = db.execute('SELECT * FROM casas WHERE usuario_id = ? ORDER BY apelido LIMIT ? OFFSET ?', (current_user.id, ITENS_POR_PAGINA, offset)).fetchall()
    return render_template('listar_casas.html', casas=casas, pagina_atual=page, total_paginas=total_paginas)

@app.route('/casas/nova')
@login_required
def pagina_cadastro_casa():
    return render_template('cadastro_casa.html')

@app.route('/casas/cadastrar', methods=['POST'])
@login_required
def cadastrar_casa():
    apelido, endereco, valor = request.form['apelido'], request.form['endereco'], request.form['valor_aluguel']
    db = get_db()
    casa_existente = db.execute('SELECT id FROM casas WHERE LOWER(apelido) = LOWER(?) AND usuario_id = ?', (apelido, current_user.id)).fetchone()
    if casa_existente:
        flash('Você já cadastrou uma casa com este apelido.', 'danger')
        return redirect(url_for('pagina_cadastro_casa'))
    db.execute('INSERT INTO casas (apelido, endereco, valor_aluguel, usuario_id) VALUES (?, ?, ?, ?)', (apelido, endereco, valor, current_user.id))
    db.commit()
    flash('Casa cadastrada com sucesso!', 'success')
    return redirect(url_for('listar_casas'))

@app.route('/casas/editar/<int:casa_id>', methods=['GET', 'POST'])
@login_required
def pagina_editar_casa(casa_id):
    db = get_db()
    casa = db.execute('SELECT * FROM casas WHERE id = ? AND usuario_id = ?', (casa_id, current_user.id)).fetchone()
    if casa is None:
        flash('Casa não encontrada ou não pertence a você.', 'danger')
        return redirect(url_for('listar_casas'))
    if request.method == 'POST':
        apelido, endereco, valor = request.form['apelido'], request.form['endereco'], request.form['valor_aluguel']
        db.execute('UPDATE casas SET apelido = ?, endereco = ?, valor_aluguel = ? WHERE id = ? AND usuario_id = ?', (apelido, endereco, valor, casa_id, current_user.id))
        db.commit()
        flash('Casa atualizada com sucesso!', 'success')
        return redirect(url_for('listar_casas'))
    return render_template('editar_casa.html', casa=casa)

@app.route('/casas/excluir/<int:casa_id>', methods=['POST'])
@login_required
def excluir_casa(casa_id):
    db = get_db()
    casa = db.execute('SELECT id FROM casas WHERE id = ? AND usuario_id = ?', (casa_id, current_user.id)).fetchone()
    if casa:
        db.execute('DELETE FROM alugueis WHERE casa_id = ?', (casa_id,))
        db.execute('DELETE FROM casas WHERE id = ?', (casa_id,))
        db.commit()
        flash('Casa e aluguéis associados foram excluídos com sucesso!', 'success')
    else:
        flash('Operação não permitida.', 'danger')
    return redirect(url_for('listar_casas'))

@app.route('/inquilinos')
@login_required
def listar_inquilinos():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    ITENS_POR_PAGINA = 10
    offset = (page - 1) * ITENS_POR_PAGINA
    total_inquilinos = db.execute('SELECT COUNT(id) FROM inquilinos WHERE usuario_id = ?', (current_user.id,)).fetchone()[0]
    total_paginas = math.ceil(total_inquilinos / ITENS_POR_PAGINA)
    inquilinos = db.execute('SELECT * FROM inquilinos WHERE usuario_id = ? ORDER BY nome LIMIT ? OFFSET ?', (current_user.id, ITENS_POR_PAGINA, offset)).fetchall()
    return render_template('listar_inquilinos.html', inquilinos=inquilinos, pagina_atual=page, total_paginas=total_paginas)

@app.route('/inquilinos/novo')
@login_required
def pagina_cadastro_inquilino():
    return render_template('cadastro_inquilino.html')

@app.route('/inquilinos/cadastrar', methods=['POST'])
@login_required
def cadastrar_inquilino():
    nome, telefone = request.form['nome'], request.form['telefone']
    db = get_db()
    inquilino_existente = db.execute('SELECT id FROM inquilinos WHERE LOWER(nome) = LOWER(?) AND usuario_id = ?', (nome, current_user.id)).fetchone()
    if inquilino_existente:
        flash('Você já cadastrou um inquilino com este nome.', 'danger')
        return redirect(url_for('pagina_cadastro_inquilino'))
    db.execute('INSERT INTO inquilinos (nome, telefone, usuario_id) VALUES (?, ?, ?)', (nome, telefone, current_user.id))
    db.commit()
    flash('Inquilino cadastrado com sucesso!', 'success')
    return redirect(url_for('listar_inquilinos'))

@app.route('/inquilinos/editar/<int:inquilino_id>', methods=['GET', 'POST'])
@login_required
def pagina_editar_inquilino(inquilino_id):
    db = get_db()
    inquilino = db.execute('SELECT * FROM inquilinos WHERE id = ? AND usuario_id = ?', (inquilino_id, current_user.id)).fetchone()
    if inquilino is None:
        flash('Inquilino não encontrado ou não pertence a você.', 'danger')
        return redirect(url_for('listar_inquilinos'))
    if request.method == 'POST':
        nome, telefone = request.form['nome'], request.form['telefone']
        db.execute('UPDATE inquilinos SET nome = ?, telefone = ? WHERE id = ? AND usuario_id = ?', (nome, telefone, inquilino_id, current_user.id))
        db.commit()
        flash('Inquilino atualizado com sucesso!', 'success')
        return redirect(url_for('listar_inquilinos'))
    return render_template('editar_inquilino.html', inquilino=inquilino)

@app.route('/inquilinos/excluir/<int:inquilino_id>', methods=['POST'])
@login_required
def excluir_inquilino(inquilino_id):
    db = get_db()
    inquilino = db.execute('SELECT id FROM inquilinos WHERE id = ? AND usuario_id = ?', (inquilino_id, current_user.id)).fetchone()
    if inquilino:
        db.execute('UPDATE alugueis SET inquilino_id = NULL WHERE inquilino_id = ?', (inquilino_id,))
        db.execute('DELETE FROM inquilinos WHERE id = ?', (inquilino_id,))
        db.commit()
        flash('Inquilino excluído com sucesso!', 'success')
    else:
        flash('Operação não permitida.', 'danger')
    return redirect(url_for('listar_inquilinos'))

@app.route('/alugueis')
@login_required
def pagina_alugueis():
    db = get_db()
    casas = db.execute('SELECT id, apelido FROM casas WHERE usuario_id = ? ORDER BY apelido', (current_user.id,)).fetchall()
    inquilinos = db.execute('SELECT id, nome FROM inquilinos WHERE usuario_id = ? ORDER BY nome', (current_user.id,)).fetchall()
    return render_template('alugueis.html', casas=casas, inquilinos=inquilinos)

@app.route('/alugueis/registrar', methods=['POST'])
@login_required
def registrar_aluguel():
    db = get_db()
    cursor = db.cursor()
    casa_id, inquilino_id, data_vencimento = request.form['casa_id'], request.form['inquilino_id'], request.form['data_vencimento']
    valor_aluguel = db.execute("SELECT valor_aluguel FROM casas WHERE id = ?", (casa_id,)).fetchone()['valor_aluguel']
    cursor.execute('INSERT INTO alugueis (casa_id, inquilino_id, data_vencimento, valor_aluguel) VALUES (?, ?, ?, ?)', (casa_id, inquilino_id, data_vencimento, valor_aluguel))
    aluguel_id = cursor.lastrowid
    if 'documento' in request.files:
        file = request.files['documento']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            cursor.execute('INSERT INTO documentos (aluguel_id, nome_original, nome_seguro) VALUES (?, ?, ?)',(aluguel_id, filename, unique_filename))
    db.commit()
    flash('Aluguel registado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/alugueis/pagar/<int:aluguel_id>', methods=['POST'])
@login_required
def dar_baixa(aluguel_id):
    db = get_db()
    db.execute('UPDATE alugueis SET pago = 1 WHERE id = ?', (aluguel_id,))
    db.commit()
    flash('Aluguel marcado como pago!', 'info')
    return redirect(url_for('index'))

@app.route('/alugueis/excluir/<int:aluguel_id>', methods=['POST'])
@login_required
def excluir_aluguel(aluguel_id):
    db = get_db()
    db.execute('DELETE FROM alugueis WHERE id = ?', (aluguel_id,))
    db.commit()
    flash('Aluguel excluído com sucesso!', 'success')
    return redirect(url_for('index'))

# --- ROTAS DE CONTRATOS ---
@app.route('/contratos')
@login_required
def listar_contratos():
    db = get_db()
    contratos_db = db.execute("""
        SELECT con.*, c.apelido as apelido_casa, i.nome as nome_inquilino
        FROM contratos con JOIN casas c ON con.casa_id = c.id JOIN inquilinos i ON con.inquilino_id = i.id
        WHERE con.usuario_id = ? ORDER BY con.status, con.data_inicio DESC
    """, (current_user.id,)).fetchall()
    contratos = []
    for c in contratos_db:
        contrato_dict = dict(c)
        contrato_dict['data_inicio_br'] = datetime.strptime(c['data_inicio'], '%Y-%m-%d').strftime('%d/%m/%Y')
        contrato_dict['data_fim_br'] = datetime.strptime(c['data_fim'], '%Y-%m-%d').strftime('%d/%m/%Y') if c['data_fim'] else None
        contratos.append(contrato_dict)
    return render_template('listar_contratos.html', contratos=contratos)

@app.route('/contratos/novo', methods=['GET', 'POST'])
@login_required
def pagina_cadastro_contrato():
    db = get_db()
    if request.method == 'POST':
        casa_id, inquilino_id = request.form['casa_id'], request.form['inquilino_id']
        valor_aluguel, dia_vencimento = request.form['valor_aluguel'], request.form['dia_vencimento']
        data_inicio, data_fim = request.form['data_inicio'], request.form.get('data_fim') or None
        contrato_existente = db.execute('SELECT id FROM contratos WHERE casa_id = ? AND status = "ativo"', (casa_id,)).fetchone()
        if contrato_existente:
            flash('Esta casa já possui um contrato ativo.', 'danger')
            return redirect(url_for('pagina_cadastro_contrato'))
        db.execute("INSERT INTO contratos (casa_id, inquilino_id, valor_aluguel, dia_vencimento, data_inicio, data_fim, usuario_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (casa_id, inquilino_id, valor_aluguel, dia_vencimento, data_inicio, data_fim, current_user.id))
        db.commit()
        flash('Contrato criado com sucesso!', 'success')
        return redirect(url_for('listar_contratos'))
    casas = db.execute('SELECT id, apelido FROM casas WHERE usuario_id = ? ORDER BY apelido', (current_user.id,)).fetchall()
    inquilinos = db.execute('SELECT id, nome FROM inquilinos WHERE usuario_id = ? ORDER BY nome', (current_user.id,)).fetchall()
    return render_template('cadastro_contrato.html', casas=casas, inquilinos=inquilinos)

@app.route('/contratos/gerar', methods=['POST'])
@login_required
def gerar_cobrancas_mensais():
    db = get_db()
    hoje = date.today()
    mes_ano_atual = hoje.strftime('%Y-%m')
    cobrancas_geradas = 0
    contratos_ativos = db.execute("SELECT * FROM contratos WHERE usuario_id = ? AND status = 'ativo'", (current_user.id,)).fetchall()
    for contrato in contratos_ativos:
        data_inicio = datetime.strptime(contrato['data_inicio'], '%Y-%m-%d').date()
        data_fim = datetime.strptime(contrato['data_fim'], '%Y-%m-%d').date() if contrato['data_fim'] else None
        contrato_valido_no_mes = True
        if data_inicio.strftime('%Y-%m') > mes_ano_atual:
            contrato_valido_no_mes = False
        if data_fim and data_fim.strftime('%Y-%m') < mes_ano_atual:
            contrato_valido_no_mes = False
        if contrato_valido_no_mes:
            data_vencimento = date(hoje.year, hoje.month, int(contrato['dia_vencimento']))
            data_vencimento_str = data_vencimento.strftime('%Y-%m-%d')
            cobrança_existente = db.execute("SELECT id FROM alugueis WHERE casa_id = ? AND strftime('%Y-%m', data_vencimento) = ?", (contrato['casa_id'], mes_ano_atual)).fetchone()
            if not cobrança_existente:
                db.execute("INSERT INTO alugueis (casa_id, inquilino_id, data_vencimento, valor_aluguel) VALUES (?, ?, ?, ?)",
                           (contrato['casa_id'], contrato['inquilino_id'], data_vencimento_str, contrato['valor_aluguel']))
                cobrancas_geradas += 1
    if cobrancas_geradas > 0:
        db.commit()
        flash(f'{cobrancas_geradas} nova(s) cobrança(s) de aluguer foram geradas para este mês!', 'success')
    else:
        flash('Nenhuma nova cobrança a ser gerada. Todas as cobranças para o mês atual já existem.', 'info')
    return redirect(url_for('index'))

@app.route('/contratos/editar/<int:contrato_id>', methods=['GET', 'POST'])
@login_required
def editar_contrato(contrato_id):
    db = get_db()
    contrato = db.execute("""
        SELECT con.*, c.apelido as apelido_casa, i.nome as nome_inquilino
        FROM contratos con
        JOIN casas c ON con.casa_id = c.id
        JOIN inquilinos i ON con.inquilino_id = i.id
        WHERE con.id = ? AND con.usuario_id = ?
    """, (contrato_id, current_user.id)).fetchone()
    if contrato is None:
        flash('Contrato não encontrado ou não pertence a você.', 'danger')
        return redirect(url_for('listar_contratos'))
    if request.method == 'POST':
        valor_aluguel, dia_vencimento = request.form['valor_aluguel'], request.form['dia_vencimento']
        data_inicio, data_fim = request.form['data_inicio'], request.form.get('data_fim') or None
        db.execute("""
            UPDATE contratos SET valor_aluguel = ?, dia_vencimento = ?, data_inicio = ?, data_fim = ?
            WHERE id = ?
        """, (valor_aluguel, dia_vencimento, data_inicio, data_fim, contrato_id))
        db.commit()
        flash('Contrato atualizado com sucesso!', 'success')
        return redirect(url_for('listar_contratos'))
    return render_template('editar_contrato.html', contrato=contrato)

@app.route('/contratos/encerrar/<int:contrato_id>', methods=['POST'])
@login_required
def encerrar_contrato(contrato_id):
    db = get_db()
    contrato = db.execute('SELECT id FROM contratos WHERE id = ? AND usuario_id = ?', (contrato_id, current_user.id)).fetchone()
    if contrato:
        db.execute("UPDATE contratos SET status = 'encerrado' WHERE id = ?", (contrato_id,))
        db.commit()
        flash('Contrato encerrado com sucesso.', 'success')
    else:
        flash('Operação não permitida.', 'danger')
    return redirect(url_for('listar_contratos'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
