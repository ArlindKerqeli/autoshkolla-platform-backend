import os
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.utils.db import init_db
from app.middleware.request_id import init_request_id
from app.middleware.response_envelope import init_response_envelope
from app.middleware.error_handler import init_error_handlers
from app.middleware.auth_context import init_auth_context
from app.middleware.api_auth_guard import init_api_auth_guard
from app.api import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config.get('SECRET_KEY')

    # Enable CORS for frontend. Supports comma-separated origins (prod, preview, localhost).
    cors_origins = Config.cors_origins() or ['http://localhost:3000']
    CORS(app, origins=cors_origins,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Request-Id'],
         expose_headers=['X-Request-Id'])

    from app.utils.serialization import json_default
    app.json.default = json_default

    init_db(app)
    init_request_id(app)
    init_auth_context(app)
    init_api_auth_guard(app)
    init_response_envelope(app)
    init_error_handlers(app)

    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Register CLI commands
    from app.seeds.seed_locations import register_seed_commands
    register_seed_commands(app)
    from app.seeds.seed_users import register_user_seed_commands
    register_user_seed_commands(app)

    return app
