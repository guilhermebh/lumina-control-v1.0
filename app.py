import sqlite3
import os
from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
import hashlib
from functools import wraps

# Configuração do Flask
# Definimos static_folder='.' para que ele busque arquivos HTML/CSS na raiz do projeto
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, supports_credentials=True)
app.secret_key = 'lumina_secret_key_2024'

# Caminho absoluto para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "lumina.db")

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def verificar_autenticacao(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "Não autenticado"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ─── Rotas de Páginas (Frontend) ───
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/login.html')
def serve_login():
    return send_from_directory('.', 'login.html')

@app.route('/dashboard.html')
def serve_dashboard():
    return send_from_directory('.', 'dashboard.html')

# Captura arquivos estáticos (CSS, JS, Imagens) ou redireciona para o index
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(BASE_DIR, path)):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

# ─── API Routes ───
@app.route('/metricas', methods=['GET'])
def obter_metricas():
    try:
        conn = get_db_connection()
        dados = conn.execute("SELECT valor, custo FROM ensaios").fetchall()
        conn.close()

        if not dados:
            return jsonify({"ticket_medio": "R$ 0,00", "roi_total": "0%", "total_projetos": 0})

        total_receita = sum(d['valor'] for d in dados)
        total_custo = sum(d['custo'] for d in dados)

        ticket = total_receita / len(dados)
        roi = ((total_receita - total_custo) / total_custo) * 100 if total_custo > 0 else 0

        return jsonify({
            "ticket_medio": f"R$ {ticket:,.2f}",
            "roi_total": f"{roi:.1f}%",
            "total_projetos": len(dados)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    senha = data.get('senha', '')

    if not email or not senha:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    conn = get_db_connection()
    usuario = conn.execute(
        "SELECT id, nome, email FROM usuarios WHERE email = ? AND senha = ?",
        (email, hash_senha(senha))
    ).fetchone()
    conn.close()

    if usuario:
        session['usuario_id'] = usuario['id']
        session['nome_usuario'] = usuario['nome']
        session['email_usuario'] = usuario['email']
        return jsonify({
            "sucesso": True,
            "usuario_id": usuario['id'],
            "nome": usuario['nome']
        }), 200
    else:
        return jsonify({"error": "Email ou senha inválidos"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"sucesso": True}), 200

@app.route('/usuario/perfil', methods=['GET'])
@verificar_autenticacao
def obter_perfil():
    usuario_id = session.get('usuario_id')
    conn = get_db_connection()
    usuario = conn.execute(
        "SELECT id, nome, email FROM usuarios WHERE id = ?",
        (usuario_id,)
    ).fetchone()
    conn.close()

    if usuario:
        return jsonify({
            "id": usuario['id'],
            "nome": usuario['nome'],
            "email": usuario['email']
        }), 200
    else:
        return jsonify({"error": "Usuário não encontrado"}), 404

@app.route('/usuario/ensaios', methods=['GET'])
@verificar_autenticacao
def obter_ensaios_usuario():
    usuario_id = session.get('usuario_id')
    conn = get_db_connection()
    ensaios = conn.execute(
        "SELECT id, valor, custo, foto_url, descricao, data_criacao FROM ensaios WHERE usuario_id = ? ORDER BY data_criacao DESC",
        (usuario_id,)
    ).fetchall()
    conn.close()

    resultado = []
    for ensaio in ensaios:
        custo = ensaio['custo'] if ensaio['custo'] else 0
        valor = ensaio['valor'] if ensaio['valor'] else 0
        roi = ((valor - custo) / custo * 100) if custo > 0 else 0
        resultado.append({
            "id": ensaio['id'],
            "valor": valor,
            "custo": custo,
            "foto_url": ensaio['foto_url'] or '',
            "descricao": ensaio['descricao'] or '',
            "roi": f"{roi:.1f}%",
            "data_criacao": ensaio['data_criacao']
        })

    return jsonify(resultado), 200

@app.route('/ensaios', methods=['POST'])
def adicionar_ensaio():
    data = request.get_json()

    if not data or 'valor' not in data or 'custo' not in data:
        return jsonify({"error": "Campos 'valor' e 'custo' são obrigatórios"}), 400

    try:
        valor = float(data['valor'])
        custo = float(data['custo'])
    except ValueError:
        return jsonify({"error": "Valores devem ser numéricos"}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO ensaios (valor, custo) VALUES (?, ?)", (valor, custo))
        conn.commit()
        return jsonify({"message": "Ensaio adicionado com sucesso"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"Erro ao adicionar ensaio: {str(e)}"}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    print("\nLumina Control - Servidor iniciado!")
    print("Acesse: http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
