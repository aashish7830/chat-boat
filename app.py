import os
import json
import uuid
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Django setup
import django
from django.conf import settings

# Django settings configuration
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(os.path.dirname(__file__), 'db.sqlite3'),
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'corsheaders',
            'rest_framework',
            __name__,  # Include current module as app
        ],
        MIDDLEWARE=[
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ],
        ROOT_URLCONF=__name__,
        CORS_ALLOW_ALL_ORIGINS=True,
        CORS_ALLOW_CREDENTIALS=True,
        ALLOWED_HOSTS=['*'],
        USE_TZ=True,
    )

# Initialize Django
django.setup()

# Now import Django components after setup
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import path, include
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

# Django Models
class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_message = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['-timestamp']

class KnowledgeBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=100, default='api')
    
    class Meta:
        db_table = 'knowledge_base'
        ordering = ['-created_at']

# Django Admin
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_message', 'ai_response', 'timestamp', 'session_id']
    list_filter = ['timestamp', 'session_id']
    search_fields = ['user_message', 'ai_response']
    readonly_fields = ['id', 'timestamp']

class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'source', 'created_at']
    list_filter = ['source', 'created_at']
    search_fields = ['text']
    readonly_fields = ['id', 'created_at']

admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(KnowledgeBase, KnowledgeBaseAdmin)

# Create database tables manually
try:
    from django.db import connection
    with connection.cursor() as cursor:
        # Create tables manually
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id VARCHAR(36) PRIMARY KEY,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                session_id VARCHAR(100)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id VARCHAR(36) PRIMARY KEY,
                text TEXT NOT NULL,
                metadata TEXT,
                created_at DATETIME NOT NULL,
                source VARCHAR(100) DEFAULT 'api'
            )
        """)
        connection.commit()
except Exception as e:
    print(f"Database setup warning: {e}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize OpenAI
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Django Views
@csrf_exempt
@require_http_methods(["POST"])
def django_chat(request):
    """Django chat view"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Search for relevant context from Django knowledge base
        context = ""
        knowledge_items = KnowledgeBase.objects.all()
        for item in knowledge_items:
            if any(word.lower() in item.text.lower() for word in user_message.lower().split()):
                context += item.text + "\n"
        
        # Create system prompt with context
        system_prompt = f"""You are Collegemate, a helpful AI assistant for college students. 
        Use the following context to provide accurate and helpful responses:
        
        Context: {context}
        
        If the context doesn't contain relevant information, provide general helpful advice for college students.
        Be friendly, supportive, and educational."""
        
        # Generate response using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Save to Django database
        chat_message = ChatMessage.objects.create(
            user_message=user_message,
            ai_response=ai_response,
            session_id=data.get('session_id', '')
        )
        
        return JsonResponse({
            'response': ai_response,
            'timestamp': chat_message.timestamp.isoformat(),
            'message_id': str(chat_message.id)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def django_ingest(request):
    """Django ingest view"""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        metadata = data.get('metadata', {})
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        # Add timestamp to metadata
        metadata['timestamp'] = timezone.now().isoformat()
        metadata['source'] = metadata.get('source', 'api')
        
        # Store in Django database
        knowledge_item = KnowledgeBase.objects.create(
            text=text,
            metadata=metadata,
            source=metadata.get('source', 'api')
        )
        
        return JsonResponse({
            'message': 'Text successfully ingested',
            'id': str(knowledge_item.id),
            'timestamp': knowledge_item.created_at.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def django_health(request):
    """Django health check"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'framework': 'Django + Flask'
    })

@require_http_methods(["GET"])
def django_stats(request):
    """Django stats view"""
    try:
        chat_count = ChatMessage.objects.count()
        knowledge_count = KnowledgeBase.objects.count()
        return JsonResponse({
            'total_chat_messages': chat_count,
            'total_knowledge_items': knowledge_count,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Django URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('django/chat/', django_chat, name='django_chat'),
    path('django/ingest/', django_ingest, name='django_ingest'),
    path('django/health/', django_health, name='django_health'),
    path('django/stats/', django_stats, name='django_stats'),
]

# Flask Routes (Updated to use Django models)
@app.route('/chat', methods=['POST'])
def chat():
    """
    Flask chat endpoint that uses Django models
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Search for relevant context from Django knowledge base
        context = ""
        knowledge_items = KnowledgeBase.objects.all()
        for item in knowledge_items:
            if any(word.lower() in item.text.lower() for word in user_message.lower().split()):
                context += item.text + "\n"
        
        # Create system prompt with context
        system_prompt = f"""You are Collegemate, a helpful AI assistant for college students. 
        Use the following context to provide accurate and helpful responses:
        
        Context: {context}
        
        If the context doesn't contain relevant information, provide general helpful advice for college students.
        Be friendly, supportive, and educational."""
        
        # Generate response using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Save to Django database
        chat_message = ChatMessage.objects.create(
            user_message=user_message,
            ai_response=ai_response,
            session_id=data.get('session_id', '')
        )
        
        return jsonify({
            'response': ai_response,
            'timestamp': chat_message.timestamp.isoformat(),
            'message_id': str(chat_message.id),
            'framework': 'Flask + Django'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ingest', methods=['POST'])
def ingest():
    """
    Flask ingest endpoint that uses Django models
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        metadata = data.get('metadata', {})
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Add timestamp to metadata
        metadata['timestamp'] = timezone.now().isoformat()
        metadata['source'] = metadata.get('source', 'api')
        
        # Store in Django database
        knowledge_item = KnowledgeBase.objects.create(
            text=text,
            metadata=metadata,
            source=metadata.get('source', 'api')
        )
        
        return jsonify({
            'message': 'Text successfully ingested',
            'id': str(knowledge_item.id),
            'timestamp': knowledge_item.created_at.isoformat(),
            'framework': 'Flask + Django'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Flask health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'framework': 'Flask + Django'
    })

@app.route('/stats', methods=['GET'])
def stats():
    """
    Flask stats endpoint using Django models
    """
    try:
        chat_count = ChatMessage.objects.count()
        knowledge_count = KnowledgeBase.objects.count()
        return jsonify({
            'total_chat_messages': chat_count,
            'total_knowledge_items': knowledge_count,
            'timestamp': timezone.now().isoformat(),
            'framework': 'Flask + Django'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Additional Flask routes for Django admin access
@app.route('/admin/', methods=['GET'])
def flask_admin_redirect():
    """Redirect to Django admin"""
    from flask import redirect
    return redirect('/admin/')

@app.route('/django/', methods=['GET'])
def django_info():
    """Django framework information"""
    return jsonify({
        'framework': 'Django + Flask',
        'django_urls': [
            '/admin/ - Django Admin Interface',
            '/django/chat/ - Django Chat API',
            '/django/ingest/ - Django Ingest API',
            '/django/health/ - Django Health Check',
            '/django/stats/ - Django Statistics'
        ],
        'flask_urls': [
            '/chat - Flask Chat API',
            '/ingest - Flask Ingest API', 
            '/health - Flask Health Check',
            '/stats - Flask Statistics'
        ]
    })

if __name__ == '__main__':
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
    
    # Skip Django admin setup for now
    print("Django admin setup skipped - using Flask + Django models only")
    
    print("\nStarting Collegemate with Flask + Django Integration")
    print("Flask API: http://localhost:5000")
    print("Django Admin: http://localhost:5000/admin/")
    print("Django API: http://localhost:5000/django/")
    print("Frontend: Open frontend/index.html in your browser")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
