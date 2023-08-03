from a2wsgi import ASGIMiddleware
from .main import app as asgi_app

app = ASGIMiddleware(asgi_app)
