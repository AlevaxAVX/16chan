import os
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "16chan_secret_key_ultra_secure"

# --- CONFIGURATION & DONNÉES ---
# Dans une application réelle, nous utiliserions SQLAlchemy ou une base de données NoSQL.
# Pour cette démonstration, nous utilisons une structure en mémoire.
threads = []
# Structure d'un thread : 
# {
#   'id': int,
#   'title': str,
#   'author': str,
#   'content': str,
#   'image_url': str,
#   'timestamp': str,
#   'replies': [ { 'author': str, 'content': str, 'timestamp': str }, ... ]
# }

# --- ROUTES ---

@app.route('/')
def index():
    """Page d'accueil affichant tous les fils de discussion."""
    # On affiche les threads du plus récent au plus ancien
    sorted_threads = sorted(threads, key=lambda x: x['id'], reverse=True)
    return render_template('index.html', threads=sorted_threads)

@app.route('/post', methods=['POST'])
def post_thread():
    """Créer un nouveau fil de discussion."""
    title = request.form.get('title')
    author = request.form.get('author') or "Anonyme"
    content = request.form.get('content')
    image_url = request.form.get('image_url')

    if not title or not content:
        flash("Le titre et le contenu sont obligatoires !", "error")
        return redirect(url_for('index'))

    new_thread = {
        'id': int(time.time()),
        'title': title,
        'author': author,
        'content': content,
        'image_url': image_url,
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'replies': []
    }

    threads.append(new_thread)
    flash("Fil de discussion créé avec succès !", "success")
    return redirect(url_for('index'))

@app.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def view_thread(thread_id):
    """Voir un thread spécifique et y répondre."""
    thread = next((t for t in threads if t['id'] == thread_id), None)
    
    if not thread:
        return "Thread non trouvé", 404

    if request.method == 'POST':
        author = request.form.get('author') or "Anonyme"
        content = request.form.get('content')

        if content:
            reply = {
                'author': author,
                'content': content,
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            thread['replies'].append(reply)
            return redirect(url_for('view_thread', thread_id=thread_id))

    return render_template('thread.html', thread=thread)

# --- TEMPLATES (Intégrés via chaines de caractères pour le fonctionnement monolithique) ---

# Note : Dans un vrai projet, ces fichiers seraient dans un dossier /templates/
index_html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>16chan - Le Réseau Libre</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #1a1a1a; color: #00ff41; font-family: 'Courier New', Courier, monospace; }
        .card { background-color: #262626; border: 1px solid #333; transition: transform 0.2s; }
        .card:hover { border-color: #00ff41; }
        input, textarea { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 10px; width: 100%; }
        .btn { background: #00ff41; color: #000; font-weight: bold; padding: 10px 20px; cursor: pointer; }
        .btn:hover { background: #00cc33; }
        .meta { color: #888; font-size: 0.8rem; }
    </style>
</head>
<body class="p-4 md:p-8">
    <header class="text-center mb-10">
        <h1 class="text-6xl font-black mb-2 tracking-tighter">16CHAN</h1>
        <p class="text-gray-500 italic">"L'underground commence ici."</p>
    </header>

    <div class="max-w-4xl mx-auto">
        <!-- Formulaire de Post -->
        <section class="mb-12 p-6 border-2 border-dashed border-green-900 rounded-lg">
            <h2 class="text-2xl mb-4 uppercase">Démarrer un nouveau thread</h2>
            <form action="/post" method="POST" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <input type="text" name="author" placeholder="Nom d'utilisateur (Optionnel)">
                    <input type="text" name="title" placeholder="Sujet du message" required>
                </div>
                <input type="url" name="image_url" placeholder="URL d'une image (Optionnel)">
                <textarea name="content" rows="4" placeholder="Votre message..." required></textarea>
                <button type="submit" class="btn w-full">PUBLIER SUR LE BOARD</button>
            </form>
        </section>

        <!-- Liste des Threads -->
        <div class="space-y-8">
            {% for thread in threads %}
            <article class="card p-6 rounded shadow-xl">
                <div class="flex flex-col md:flex-row gap-6">
                    {% if thread.image_url %}
                    <div class="md:w-1/3">
                        <img src="{{ thread.image_url }}" alt="Post image" class="rounded border border-gray-700 w-full object-cover h-48">
                    </div>
                    {% endif %}
                    <div class="flex-1">
                        <header class="mb-2">
                            <span class="meta">No.{{ thread.id }} | Par {{ thread.author }} le {{ thread.timestamp }}</span>
                            <h3 class="text-2xl font-bold text-white">{{ thread.title }}</h3>
                        </header>
                        <p class="text-gray-300 mb-4 whitespace-pre-wrap">{{ thread.content[:300] }}{% if thread.content|length > 300 %}...{% endif %}</p>
                        <a href="/thread/{{ thread.id }}" class="text-green-400 hover:underline">Voir les {{ thread.replies|length }} réponses >></a>
                    </div>
                </div>
            </article>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

thread_html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>16chan - {{ thread.title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #1a1a1a; color: #00ff41; font-family: 'Courier New', Courier, monospace; }
        .card { background-color: #262626; border: 1px solid #333; }
        .reply-card { background-color: #2d2d2d; border-left: 4px solid #00ff41; margin-left: 20px; padding: 15px; }
        input, textarea { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 10px; width: 100%; }
        .btn { background: #00ff41; color: #000; font-weight: bold; padding: 10px 20px; cursor: pointer; }
        .meta { color: #888; font-size: 0.8rem; }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-4xl mx-auto">
        <a href="/" class="text-green-400 mb-6 inline-block underline underline-offset-4 hover:text-white"><< Retour à l'accueil</a>
        
        <!-- Thread Principal -->
        <article class="card p-8 rounded-lg shadow-2xl mb-8">
            <div class="meta mb-4 text-xs uppercase tracking-widest">Initial Post - {{ thread.timestamp }}</div>
            <h1 class="text-4xl font-bold text-white mb-6 border-b border-green-900 pb-2">{{ thread.title }}</h1>
            
            {% if thread.image_url %}
            <div class="mb-6">
                <img src="{{ thread.image_url }}" alt="Image" class="max-h-96 rounded mx-auto border border-gray-600">
            </div>
            {% endif %}
            
            <p class="text-xl text-gray-200 leading-relaxed whitespace-pre-wrap mb-4">{{ thread.content }}</p>
            <div class="text-sm italic text-gray-500 text-right">Posté par: {{ thread.author }}</div>
        </article>

        <!-- Réponses -->
        <div class="space-y-4 mb-10">
            <h2 class="text-xl border-l-2 border-green-500 pl-4 mb-6">RÉPONSES ({{ thread.replies|length }})</h2>
            {% for reply in thread.replies %}
            <div class="reply-card rounded">
                <div class="meta mb-2">Anonyme (ID: {{ loop.index }}) | {{ reply.timestamp }}</div>
                <p class="text-gray-300">{{ reply.content }}</p>
            </div>
            {% endfor %}
        </div>

        <!-- Formulaire de Réponse -->
        <section class="card p-6 rounded-lg sticky bottom-4">
            <h3 class="text-lg mb-4">Ajouter une réponse</h3>
            <form action="/thread/{{ thread.id }}" method="POST" class="space-y-3">
                <input type="text" name="author" placeholder="Votre pseudonyme (Optionnel)">
                <textarea name="content" rows="3" placeholder="Tapez votre réponse ici..." required></textarea>
                <button type="submit" class="btn w-full">RÉPONDRE</button>
            </form>
        </section>
    </div>
</body>
</html>
"""

# Injection des templates dans le moteur Flask
# Note: Pour un script simple, nous utilisons une astuce pour ne pas créer de dossiers.
from flask import render_template_string

@app.after_request
def after_request(response):
    return response

# On surcharge la fonction de rendu pour utiliser nos chaines HTML
@app.context_processor
def inject_template_logic():
    def custom_render(template_name, **context):
        if template_name == 'index.html':
            return render_template_string(index_html, **context)
        elif template_name == 'thread.html':
            return render_template_string(thread_html, **context)
        return "Template non trouvé"
    return dict(render_template=custom_render)

if __name__ == '__main__':
    # Initialisation de quelques données de démo
    threads.append({
        'id': 1,
        'title': 'Bienvenue sur 16chan !',
        'author': 'Admin',
        'content': 'Ceci est le premier message du réseau social 16chan. Respectez les règles et amusez-vous bien dans les limbes du web.',
        'image_url': 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=1000&auto=format&fit=crop',
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'replies': [
            {'author': 'UserX', 'content': 'Enfin un endroit libre !', 'timestamp': 'Aujourd\'hui 12:00'}
        ]
    })
    
    # Lancement de l'application
    # Host 0.0.0.0 pour être accessible sur le réseau local
    app.run(debug=True, port=5000)
