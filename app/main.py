from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Import and register blueprints
    from app.routes.generate import generate_bp
    from app.routes.improve import improve_bp
    
    app.register_blueprint(generate_bp)
    app.register_blueprint(improve_bp)
    
    @app.route('/')
    def hello():
        return jsonify({
            "message": "🧭 DTV Assistant API is running!",
            "version": "1.0.0",
            "endpoints": [
                "POST /generate-reply",
                "POST /improve-ai",
                "POST /improve-ai-manually"
            ]
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    app.run(host='0.0.0.0', port=port, debug=True)