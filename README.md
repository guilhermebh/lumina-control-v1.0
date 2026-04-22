# Lumina Control - Sistema de Gestão de Ensaios com Login Social

Um dashboard moderno para gerenciar resultados de ensaios com sistema de autenticação e compartilhamento em redes sociais.

## 🚀 Funcionalidades

✅ **Painel de Administração**
- Dashboard com métricas em tempo real
- Ticket médio, ROI global e contagem de projetos
- Adicionar novos ensaios com valor e custo

✅ **Sistema de Login para Clientes**
- Autenticação segura com email e senha
- Acesso protegido aos resultados pessoais
- Gerenciamento de sessão

✅ **Painel do Cliente**
- Visualização dos resultados de ensaios pessoais
- Exibição de fotos dos resultados
- Cálculo automático de ROI individual
- Data de criação de cada ensaio

✅ **Compartilhamento Social**
- Compartilhar resultados no Facebook
- Compartilhar no Twitter/X
- Enviar via WhatsApp
- Compartilhar no LinkedIn

## 📋 Credenciais de Teste

```
Cliente 1:
Email: cliente1@lumina.com
Senha: senha123

Cliente 2:
Email: cliente2@lumina.com
Senha: senha456

Cliente 3:
Email: cliente3@lumina.com
Senha: senha789
```

## 🛠️ Instalação

1. **Instalar dependências**
```bash
python -m pip install --user flask flask-cors
```

2. **Inicializar o banco de dados**
```bash
python init_db.py
```

3. **Executar o servidor**
```bash
python engine.py
```

O servidor estará disponível em: `http://127.0.0.1:5000`

## 📁 Estrutura do Projeto

```
LuminaProject/
├── engine.py              # Backend Flask com APIs
├── init_db.py            # Script para inicializar banco de dados
├── index.html            # Painel administrativo
├── login.html            # Página de login
├── results.html          # Painel do cliente autenticado
├── script.js             # JavaScript do dashboard
├── style.css             # Estilos CSS
├── lumina.db             # Banco de dados SQLite
└── requirements.txt      # Dependências do projeto
```

## 🔌 API Endpoints

### Públicos
- `GET /metricas` - Obter métricas globais
- `POST /login` - Autenticar usuário
- `POST /logout` - Encerrar sessão

### Protegidos (Requer autenticação)
- `GET /usuario/perfil` - Obter dados do usuário
- `GET /usuario/ensaios` - Listar ensaios do usuário
- `POST /ensaios` - Adicionar novo ensaio

## 💻 Como Usar

### Acessar o Dashboard Admin
1. Abra `http://127.0.0.1:5000/index.html`
2. Visualize as métricas globais
3. Adicione novos ensaios

### Acessar o Painel do Cliente
1. Clique em "Acessar Painel do Cliente" no dashboard
2. Login com uma das credenciais de teste
3. Visualize seus resultados
4. Compartilhe nos botões de rede social

## 🔐 Segurança

- Senhas armazenadas com hash SHA-256
- Sessões protegidas por verificação de autenticação
- CORS habilitado para requisições entre domínios

## 📱 Responsividade

- Design responsivo para desktop, tablet e mobile
- Grid automático para cards de ensaios
- Interface fluida e intuitiva

## 🔄 Próximas Melhorias

- [ ] Upload de fotos real junto com ensaios
- [ ] Sistema de notificações por email
- [ ] Dashboard com gráficos avançados
- [ ] Integração com Google Analytics
- [ ] Exportar relatórios em PDF

---

**Versão:** 1.0  
**Data:** Março de 2026  
**Desenvolvido com:** Flask, SQLite, HTML5, CSS3, JavaScript
