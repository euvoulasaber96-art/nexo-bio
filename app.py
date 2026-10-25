from flask import Flask, render_template_string, request, redirect, send_from_directory
import sqlite3
import os

# ================= INICIALIZAÇÃO DO FLASK =================
app = Flask(__name__)

# ================= BANCO DE DADOS =================
def db_query(query, params=()):
    conn = sqlite3.connect('nexo.db')
    c = conn.cursor()
    c.execute(query, params)
    res = c.fetchall()
    conn.commit()
    conn.close()
    return res

def init_db():
    db_query("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT, bio TEXT, avatar_url TEXT, theme TEXT DEFAULT 'dark', is_premium INTEGER DEFAULT 0
    )""")
    db_query("""CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, titulo TEXT, url TEXT, icon TEXT
    )""")
init_db()

# ================= ROTAS =================
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/criar', methods=['POST'])
def criar_conta():
    u = request.form.get('username')
    p = request.form.get('password')
    if not u or not p: return "Preencha tudo."
    if db_query("SELECT * FROM users WHERE username=?", (u,)): return "Nome em uso."
    db_query("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
    return redirect(f'/painel/{u}')

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('username')
    p = request.form.get('password')
    user = db_query("SELECT * FROM users WHERE username=? AND password=?", (u, p))
    if user: return redirect(f'/painel/{u}')
    return "Usuário ou senha incorretos."

@app.route('/painel/<username>')
def painel(username):
    user = db_query("SELECT * FROM users WHERE username=?", (username,))
    if not user: return "Usuário não encontrado."
    links = db_query("SELECT * FROM links WHERE username=?", (username,))
    
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Painel - {{ user[0][0] }}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body { background: #050505; color: #fff; font-family: 'Inter', sans-serif; padding: 40px; display: flex; justify-content: center; }
            .container { max-width: 800px; width: 100%; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
            .header h1 { color: #ff0055; font-size: 24px; }
            .btn-ver { background: #10b981; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 14px; }
            
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
            
            .card { background: #121216; border: 1px solid #333; border-radius: 16px; padding: 25px; margin-bottom: 20px; }
            .card h3 { margin-bottom: 15px; color: #fff; border-bottom: 1px solid #333; padding-bottom: 10px; }
            
            input, select { width: 100%; padding: 12px; margin-bottom: 15px; background: #050505; border: 1px solid #333; color: #fff; border-radius: 8px; font-family: 'Inter'; }
            input:focus { border-color: #ff0055; outline: none; }
            button { background: #ff0055; color: #fff; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; transition: 0.3s; }
            button:hover { background: #cc0044; }
            
            .link-list-item { display: flex; align-items: center; justify-content: space-between; background: #1a1a1f; padding: 12px; border-radius: 8px; margin-bottom: 8px; }
            .link-list-item i { color: #ff0055; font-size: 20px; margin-right: 15px; }
            .link-list-item a { color: #ef4444; text-decoration: none; font-size: 14px; }
            
            .premium-box { border: 1px solid #fbbf24; background: rgba(251, 191, 36, 0.05); text-align: center; }
            .premium-box h3 { color: #fbbf24; border-bottom-color: #fbbf24; }
            .btn-premium { background: #fbbf24; color: #000; margin-top: 10px; }
            .btn-premium:hover { background: #f59e0b; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Olá, @{{ user[0][0] }}</h1>
                <a href="/u/{{ user[0][0] }}" target="_blank" class="btn-ver">Ver Página Pública</a>
            </div>

            <div class="grid">
                <div>
                    <div class="card">
                        <h3>Editar Perfil</h3>
                        <form action="/update_perfil" method="POST">
                            <input type="hidden" name="username" value="{{ user[0][0] }}">
                            <label style="font-size:12px; color:#aaa;">Foto de Perfil (URL da imagem)</label>
                            <input type="text" name="avatar" placeholder="https://imgur.com/foto.png" value="{{ user[0][3] or '' }}">
                            
                            <label style="font-size:12px; color:#aaa;">Bio / Descrição</label>
                            <input type="text" name="bio" placeholder="Minha bio incrível..." value="{{ user[0][2] or '' }}">
                            
                            <button type="submit">Salvar Alterações</button>
                        </form>
                    </div>

                    <div class="card">
                        <h3>Adicionar Novo Link</h3>
                        <form action="/add_link" method="POST">
                            <input type="hidden" name="username" value="{{ user[0][0] }}">
                            <input type="text" name="titulo" placeholder="Título (Ex: Meu Instagram)" required>
                            <input type="text" name="url" placeholder="URL (Ex: https://instagram.com/...)" required>
                            
                            <select name="icon">
                                <option value="fa-link">Padrão</option>
                                <option value="fa-brands fa-instagram">Instagram</option>
                                <option value="fa-brands fa-twitch">Twitch</option>
                                <option value="fa-brands fa-youtube">YouTube</option>
                                <option value="fa-brands fa-tiktok">TikTok</option>
                                <option value="fa-brands fa-discord">Discord</option>
                            </select>
                            
                            <button type="submit">Adicionar Link</button>
                        </form>
                    </div>
                </div>

                <div>
                    <div class="card premium-box">
                        <h3>Assinatura Premium</h3>
                        <p style="font-size:14px; color:#aaa; margin-bottom:10px;">Remova o selo "Nexo.bio" e bloqueie anúncios.</p>
                        {% if user[0][5] == 1 %}
                            <p style="color:#10b981; font-weight:bold;">✅ Você é Premium!</p>
                        {% else %}
                            <button class="btn-premium" onclick="alert('Integração com Mercado Pago aqui.')">Assinar por R$ 9,90/mês</button>
                        {% endif %}
                    </div>

                    <div class="card">
                        <h3>Seus Links</h3>
                        {% for link in links %}
                            <div class="link-list-item">
                                <div style="display:flex; align-items:center;">
                                    <i class="{% if link[4] %}{{ link[4] }}{% else %}fa-solid fa-link{% endif %}"></i>
                                    <span>{{ link[2] }}</span>
                                </div>
                                <a href="/delete/{{ link[0] }}/{{ user[0][0] }}">Excluir</a>
                            </div>
                        {% else %}
                            <p style="color:#aaa; font-size:14px;">Nenhum link adicionado.</p>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """, user=user, links=links)

@app.route('/update_perfil', methods=['POST'])
def update_perfil():
    u = request.form.get('username')
    a = request.form.get('avatar')
    b = request.form.get('bio')
    db_query("UPDATE users SET avatar_url=?, bio=? WHERE username=?", (a, b, u))
    return redirect(f'/painel/{u}')

@app.route('/add_link', methods=['POST'])
def add_link():
    u = request.form.get('username')
    t = request.form.get('titulo')
    url = request.form.get('url')
    ic = request.form.get('icon')
    db_query("INSERT INTO links (username, titulo, url, icon) VALUES (?, ?, ?, ?)", (u, t, url, ic))
    return redirect(f'/painel/{u}')

@app.route('/delete/<int:id>/<username>')
def delete_link(id, username):
    db_query("DELETE FROM links WHERE id=?", (id,))
    return redirect(f'/painel/{username}')

@app.route('/u/<username>')
def pagina_publica(username):
    user = db_query("SELECT * FROM users WHERE username=?", (username,))
    if not user: return "Página não encontrada.", 404
    links = db_query("SELECT * FROM links WHERE username=?", (username,))
    
    is_premium = user[0][5] if len(user[0]) > 5 else 0

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>{{ user[0][0] }} | Nexo.bio</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: #050505; color: #fff; font-family: 'Inter', sans-serif;
                display: flex; flex-direction: column; align-items: center; min-height: 100vh;
                background: radial-gradient(circle at 50% 0%, rgba(255,0,85,0.15) 0%, #050505 60%);
                padding: 40px 20px;
            }
            .container { width: 100%; max-width: 500px; display: flex; flex-direction: column; align-items: center; }
            
            .avatar {
                width: 110px; height: 110px; border-radius: 50%; background: #121216; border: 3px solid #ff0055;
                margin-bottom: 20px; box-shadow: 0 0 30px rgba(255,0,85,0.4); object-fit: cover;
            }
            .nome { font-size: 28px; font-weight: 800; margin-bottom: 8px; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
            .bio { color: #a1a1aa; font-size: 16px; text-align: center; margin-bottom: 30px; line-height: 1.5; }
            
            .links-wrapper { width: 100%; display: flex; flex-direction: column; gap: 15px; margin-bottom: 40px; }
            .link-btn {
                background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
                color: #fff; text-decoration: none; padding: 18px 20px; border-radius: 16px;
                display: flex; align-items: center; font-weight: 600; font-size: 16px;
                transition: all 0.3s ease; backdrop-filter: blur(10px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .link-btn:hover {
                background: #ff0055; border-color: #ff0055; transform: translateY(-3px) scale(1.02);
                box-shadow: 0 10px 25px rgba(255,0,85,0.4);
            }
            .link-btn i { font-size: 22px; margin-right: 15px; width: 25px; text-align: center; }
            
            .ad-container {
                width: 100%; margin-bottom: 20px; border-radius: 12px; overflow: hidden;
                border: 1px solid #333; position: relative;
            }
            .ad-label { 
                position: absolute; top: 5px; right: 5px; background: rgba(0,0,0,0.7); 
                color: #fff; font-size: 10px; padding: 2px 5px; border-radius: 4px; 
            }
            .ad-banner img { width: 100%; height: auto; display: block; }
            
            .footer { margin-top: auto; font-size: 14px; color: #52525b; padding-top: 40px; }
            .footer a { color: #ff0055; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            {% if not is_premium %}
            <div class="ad-container">
                <span class="ad-label">Anúncio</span>
                <div class="ad-banner">
                    <a href="https://teu-link-de-anunciante.com" target="_blank">
                        <img src="https://via.placeholder.com/500x100/121216/ff0055?text=Anuncie+Sua+Marca+Aqui" alt="Ad">
                    </a>
                </div>
            </div>
            {% endif %}

            {% if user[0][3] %}
                <img src="{{ user[0][3] }}" class="avatar" alt="Avatar">
            {% else %}
                <div class="avatar" style="display:flex; align-items:center; justify-content:center; font-size:40px; font-weight:800;">{{ user[0][0][0].upper() }}</div>
            {% endif %}

            <h1 class="nome">@{{ user[0][0] }}</h1>
            <p class="bio">{{ user[0][2] if user[0][2] else 'Bem-vindo ao meu perfil!' }}</p>

            <div class="links-wrapper">
                {% for link in links %}
                    <a href="{{ link[3] }}" target="_blank" class="link-btn">
                        <i class="{% if link[4] %}{{ link[4] }}{% else %}fa-solid fa-link{% endif %}"></i>
                        {{ link[2] }}
                    </a>
                {% endfor %}
            </div>

            {% if not is_premium %}
            <div class="ad-container">
                <span class="ad-label">Anúncio</span>
                <div class="ad-banner">
                    <a href="https://teu-link-de-anunciante.com" target="_blank">
                        <img src="https://via.placeholder.com/500x100/121216/ff0055?text=Anuncie+Sua+Marca+Aqui" alt="Ad">
                    </a>
                </div>
            </div>
            {% endif %}

            <div class="footer">
                {% if is_premium %}
                    © {{ user[0][0] }}
                {% else %}
                    Feito com <a href="/">Nexo.bio</a>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, user=user, links=links, is_premium=is_premium)

if __name__ == '__main__':
    app.run(debug=True, port=5000)