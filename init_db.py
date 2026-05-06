import sqlite3
import hashlib

DB_NAME = "lumina.db"


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Criar tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            nome TEXT NOT NULL,
            role TEXT DEFAULT 'USER',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Criar tabela de ensaios com referência ao usuário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ensaios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            valor REAL NOT NULL,
            custo REAL NOT NULL,
            foto_url TEXT,
            descricao TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    # Criar tabela de solicitações de acesso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitacoes_acesso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            motivo TEXT,
            status TEXT DEFAULT 'PENDENTE',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Criar tabela de logs de auditoria
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            acao TEXT NOT NULL,
            detalhes TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Verificar se já tem usuários
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        # Inserir usuários de teste
        usuarios_teste = [
            ('cliente1@lumina.com', hash_senha('senha123'), 'João Silva', 'ADMIN'),
            ('cliente2@lumina.com', hash_senha('senha456'), 'Maria Santos', 'USER'),
            ('cliente3@lumina.com', hash_senha('senha789'), 'Pedro Oliveira', 'USER'),
        ]

        cursor.executemany(
            'INSERT INTO usuarios (email, senha, nome, role) VALUES (?, ?, ?, ?)', usuarios_teste)
        print(f"[OK] {len(usuarios_teste)} usuários criados")

    # Verificar se já tem ensaios
    cursor.execute('SELECT COUNT(*) FROM ensaios')
    ensaio_count = cursor.fetchone()[0]

    if ensaio_count == 0:
        # Inserir dados de teste para os ensaios
        dados_teste = [
            (1, 4500, 1200, 'https://via.placeholder.com/300?text=Ensaio+1',
             'Resultado positivo para o modelo A'),
            (1, 7200, 1800, 'https://via.placeholder.com/300?text=Ensaio+2',
             'Melhor performance em testes'),
            (2, 3800, 950, 'https://via.placeholder.com/300?text=Ensaio+3',
             'Teste com cliente premium'),
            (2, 6100, 1500, 'https://via.placeholder.com/300?text=Ensaio+4',
             'Resultado excepcional'),
            (3, 5300, 1100, 'https://via.placeholder.com/300?text=Ensaio+5',
             'ROI acima da média'),
        ]

        cursor.executemany(
            'INSERT INTO ensaios (usuario_id, valor, custo, foto_url, descricao) VALUES (?, ?, ?, ?, ?)', dados_teste)
        print(f"[OK] {len(dados_teste)} ensaios criados")
    else:
        print(f"[OK] Banco de dados já contém {ensaio_count} ensaios")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
