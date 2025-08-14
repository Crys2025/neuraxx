import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.blockchain import blockchain_bp
from src.routes.wallet import wallet_bp
from src.routes.tokenomics import tokenomics_bp
from core.blockchain import NeuraXBlockchain
from tokenomics.smart_contracts import NeuraXTokenomics

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'neurax_blockchain_production_key_2026'

# Enable CORS
CORS(app, origins="*")

# Initialize NeuraX blockchain and tokenomics
neurax_blockchain = NeuraXBlockchain()
neurax_tokenomics = NeuraXTokenomics()

# Make blockchain and tokenomics available to routes
app.config['NEURAX_BLOCKCHAIN'] = neurax_blockchain
app.config['NEURAX_TOKENOMICS'] = neurax_tokenomics

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
app.register_blueprint(tokenomics_bp, url_prefix='/api/tokenomics')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "NeuraX Blockchain API",
        "version": "1.0.0",
        "blockchain_status": "active",
        "tokenomics_status": "active"
    })

@app.route('/api/stats')
def get_stats():
    """Get comprehensive blockchain and tokenomics statistics"""
    try:
        blockchain_stats = neurax_blockchain.get_blockchain_stats()
        tokenomics_stats = neurax_tokenomics.get_tokenomics_stats()
        return jsonify({
            "blockchain": blockchain_stats,
            "tokenomics": tokenomics_stats,
            "timestamp": neurax_blockchain.get_current_time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve static files and frontend"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                "message": "NeuraX Blockchain API Server",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/api/health",
                    "stats": "/api/stats",
                    "blockchain": "/api/blockchain/*",
                    "wallet": "/api/wallet/*",
                    "tokenomics": "/api/tokenomics/*"
                }
            })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Starting NeuraX Blockchain API Server...")
    print("Blockchain Status:", "Active" if neurax_blockchain else "Inactive")
    print("Tokenomics Status:", "Active" if neurax_tokenomics else "Inactive")
    app.run(host='0.0.0.0', port=5000, debug=False)


