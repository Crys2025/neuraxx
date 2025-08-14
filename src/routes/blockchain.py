from flask import Blueprint, request, jsonify, current_app
from decimal import Decimal
import json

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/info', methods=['GET'])
def get_blockchain_info():
    """Get blockchain information"""
    try:
        blockchain = current_app.config['NEURAX_BLOCKCHAIN']
        
        info = {
            "chain_id": blockchain.chain_id,
            "network_name": "NeuraX Mainnet",
            "current_block": blockchain.get_latest_block_height(),
            "total_blocks": len(blockchain.blocks),
            "total_transactions": blockchain.transaction_count,
            "active_nodes": len(blockchain.nodes),
            "consensus": "Proof of Intelligence",
            "block_time": blockchain.block_time,
            "difficulty": blockchain.difficulty,
            "network_hash_rate": blockchain.get_network_hash_rate()
        }
        
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@blockchain_bp.route('/blocks', methods=['GET'])
def get_blocks():
    """Get recent blocks"""
    try:
        blockchain = current_app.config['NEURAX_BLOCKCHAIN']
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 10)), 100)
        
        # Get blocks
        total_blocks = len(blockchain.blocks)
        start_idx = max(0, total_blocks - (page * limit))
        end_idx = max(0, total_blocks - ((page - 1) * limit))
        
        blocks = []
        for i in range(end_idx - 1, start_idx - 1, -1):
            if i < len(blockchain.blocks):
                block = blockchain.blocks[i]
                blocks.append({
                    "height": block.height,
                    "hash": block.hash,
                    "previous_hash": block.previous_hash,
                    "timestamp": block.timestamp,
                    "transactions": len(block.transactions),
                    "validator": block.validator,
                    "ai_score": block.ai_validation_score,
                    "size": len(str(block))
                })
        
        return jsonify({
            "blocks": blocks,
            "total": total_blocks,
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@blockchain_bp.route('/block/<block_hash>', methods=['GET'])
def get_block(block_hash):
    """Get specific block by hash"""
    try:
        blockchain = current_app.config['NEURAX_BLOCKCHAIN']
        
        block = blockchain.get_block_by_hash(block_hash)
        if not block:
            return jsonify({"error": "Block not found"}), 404
        
        block_data = {
            "height": block.height,
            "hash": block.hash,
            "previous_hash": block.previous_hash,
            "merkle_root": block.merkle_root,
            "timestamp": block.timestamp,
            "validator": block.validator,
            "ai_validation_score": block.ai_validation_score,
            "quantum_signature": block.quantum_signature,
            "transactions": [tx.to_dict() for tx in block.transactions],
            "size": len(str(block)),
            "nonce": getattr(block, 'nonce', 0)
        }
        
        return jsonify(block_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@blockchain_bp.route('/transaction/<tx_hash>', methods=['GET'])
def get_transaction(tx_hash):
    """Get specific transaction by hash"""
    try:
        blockchain = current_app.config['NEURAX_BLOCKCHAIN']
        
        transaction = blockchain.get_transaction_by_hash(tx_hash)
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404
        
        return jsonify(transaction.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@blockchain_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """Get recent transactions"""
    try:
        blockchain = current_app.config['NEURAX_BLOCKCHAIN']
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        address = request.args.get('address')
        
        # Get transactions
        all_transactions = []
        for block in blockchain.blocks:
            for tx in block.transactions:
                if address and address not in [tx.from_address, tx.to_address]:
                    continue
                all_transactions.append(tx.to_dict())
        
        # Sort by timestamp (newest first)
        all_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Paginate
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        transactions = all_transactions[start_idx:end_idx]
        
        return jsonify({
            "transactions": transactions,
            "total": len(all_transactions),
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@blockchain_bp.route('/submit_transaction', methods=['POST'])
def submit_transaction():
    """Submit a new transaction to the blockchain"""
    try:
        blockchain = current_app.config['NEURAX_BLOCKCHAIN']
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['from_address', 'to_address', 'amount', 'private_key']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create and submit transaction
        tx_hash = blockchain.create_transaction(
            from_address=data['from_address'],
            to_address=data['to_address'],
            amount=Decimal(str(data['amount'])),
            private_key=data['private_key'],
            data=data.get('data', {})
        )
        
        if tx_hash:
            return jsonify({
                "success": True,
                "transaction_hash": tx_hash,
                "message": "Transaction submitted successfully"
            })
        else:
            return jsonify({"error": "Failed to create transaction"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@blockchain_bp.route('/validate_address', methods=['POST'])
def validate_address():
    """Validate a blockchain address"""
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({"error": "Address is required"}), 400
        
        # Basic validation (NeuraX addresses start with NX)
        is_valid = address.startswith('NX') and len(address) >= 40
        
        return jsonify({
            "address": address,
            "is_valid": is_valid,
            "format": "NeuraX" if is_valid else "Invalid"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@blockchain_bp.route('/network_stats', methods=['GET'])
def get_network_stats():
    """Get network statistics"""
    try:
        blockchain = current_app.config['NEURAX_BLOCKCHAIN']
        
        stats = {
            "total_nodes": len(blockchain.nodes),
            "active_validators": len([n for n in blockchain.nodes.values() if n.node_type == "validator"]),
            "network_hash_rate": blockchain.get_network_hash_rate(),
            "average_block_time": blockchain.block_time,
            "current_difficulty": blockchain.difficulty,
            "total_supply": str(blockchain.get_total_supply()),
            "circulating_supply": str(blockchain.get_circulating_supply()),
            "last_block_time": blockchain.get_latest_block().timestamp if blockchain.blocks else 0
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@blockchain_bp.route('/ai_validation_stats', methods=['GET'])
def get_ai_validation_stats():
    """Get AI validation statistics"""
    try:
        blockchain = current_app.config['NEURAX_BLOCKCHAIN']
        
        # Calculate AI validation statistics
        total_validations = 0
        total_score = 0
        fraud_detected = 0
        
        for block in blockchain.blocks:
            if hasattr(block, 'ai_validation_score'):
                total_validations += 1
                total_score += block.ai_validation_score
                if block.ai_validation_score < 50:  # Threshold for fraud detection
                    fraud_detected += 1
        
        avg_score = total_score / max(1, total_validations)
        
        stats = {
            "total_validations": total_validations,
            "average_ai_score": round(avg_score, 2),
            "fraud_attempts_detected": fraud_detected,
            "fraud_detection_rate": round((fraud_detected / max(1, total_validations)) * 100, 2),
            "ai_consensus_accuracy": round(avg_score, 2)
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

