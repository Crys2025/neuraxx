from flask import Blueprint, request, jsonify, current_app
from decimal import Decimal
import secrets
import hashlib
import time

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/create', methods=['POST'])
def create_wallet():
    """Create a new wallet"""
    try:
        # Generate new wallet
        private_key = secrets.token_urlsafe(32)
        
        # Generate address from private key (simplified)
        address_hash = hashlib.sha256(private_key.encode()).hexdigest()
        address = f"NX{address_hash[:38]}"
        
        # Create account in tokenomics
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        success = tokenomics.token_contract.create_account(address)
        
        if success:
            return jsonify({
                "address": address,
                "private_key": private_key,
                "balance": "0",
                "created_at": time.time(),
                "message": "Wallet created successfully"
            })
        else:
            return jsonify({"error": "Failed to create wallet"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    """Get wallet balance"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        account = tokenomics.token_contract.get_account(address)
        
        if not account:
            return jsonify({"error": "Account not found"}), 404
        
        return jsonify({
            "address": address,
            "balance": str(account.balance),
            "staked_amount": str(account.staked_amount),
            "locked_amount": str(account.locked_amount),
            "available_balance": str(account.available_balance()),
            "total_balance": str(account.total_balance()),
            "ai_score": account.ai_score,
            "reputation_score": account.reputation_score,
            "last_activity": account.last_activity
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/info/<address>', methods=['GET'])
def get_wallet_info(address):
    """Get comprehensive wallet information"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        account_info = tokenomics.get_account_info(address)
        
        if not account_info:
            return jsonify({"error": "Account not found"}), 404
        
        return jsonify(account_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/transfer', methods=['POST'])
def transfer_tokens():
    """Transfer tokens between wallets"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['from_address', 'to_address', 'amount', 'private_key']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        # Create transfer transaction
        from tokenomics.smart_contracts import TransactionType
        tx_id = tokenomics.create_transaction(
            TransactionType.TRANSFER,
            data['from_address'],
            data['to_address'],
            Decimal(str(data['amount']))
        )
        
        if tx_id:
            return jsonify({
                "success": True,
                "transaction_id": tx_id,
                "message": "Transfer completed successfully"
            })
        else:
            return jsonify({"error": "Transfer failed"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/stake', methods=['POST'])
def stake_tokens():
    """Stake tokens"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['address', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        # Create staking transaction
        from tokenomics.smart_contracts import TransactionType
        tx_data = {
            "lock_period": data.get('lock_period', 0)
        }
        
        tx_id = tokenomics.create_transaction(
            TransactionType.STAKE,
            data['address'],
            data['address'],
            Decimal(str(data['amount'])),
            tx_data
        )
        
        if tx_id:
            return jsonify({
                "success": True,
                "transaction_id": tx_id,
                "message": "Staking completed successfully"
            })
        else:
            return jsonify({"error": "Staking failed"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/unstake', methods=['POST'])
def unstake_tokens():
    """Unstake tokens"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['address', 'position_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        # Create unstaking transaction
        from tokenomics.smart_contracts import TransactionType
        tx_data = {
            "position_id": data['position_id']
        }
        
        tx_id = tokenomics.create_transaction(
            TransactionType.UNSTAKE,
            data['address'],
            data['address'],
            Decimal("0"),
            tx_data
        )
        
        if tx_id:
            return jsonify({
                "success": True,
                "transaction_id": tx_id,
                "message": "Unstaking initiated successfully"
            })
        else:
            return jsonify({"error": "Unstaking failed"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/claim_rewards', methods=['POST'])
def claim_rewards():
    """Claim staking rewards"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['address', 'position_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        # Create claim rewards transaction
        from tokenomics.smart_contracts import TransactionType
        tx_data = {
            "position_id": data['position_id']
        }
        
        tx_id = tokenomics.create_transaction(
            TransactionType.CLAIM_REWARDS,
            data['address'],
            data['address'],
            Decimal("0"),
            tx_data
        )
        
        if tx_id:
            return jsonify({
                "success": True,
                "transaction_id": tx_id,
                "message": "Rewards claimed successfully"
            })
        else:
            return jsonify({"error": "Claiming rewards failed"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/staking_positions/<address>', methods=['GET'])
def get_staking_positions(address):
    """Get staking positions for an address"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        positions = tokenomics.staking_contract.get_staking_info(address)
        
        return jsonify({
            "address": address,
            "positions": positions,
            "total_positions": len(positions),
            "total_staked": str(sum(Decimal(p['amount']) for p in positions))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/transaction_history/<address>', methods=['GET'])
def get_transaction_history(address):
    """Get transaction history for an address"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        
        # Get transactions for address
        address_transactions = [
            tx.to_dict() for tx in tokenomics.transactions.values()
            if tx.from_address == address or tx.to_address == address
        ]
        
        # Sort by timestamp (newest first)
        address_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Paginate
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        transactions = address_transactions[start_idx:end_idx]
        
        return jsonify({
            "address": address,
            "transactions": transactions,
            "total": len(address_transactions),
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/validate_transaction', methods=['POST'])
def validate_transaction():
    """Validate a transaction using AI"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['validator_address', 'transaction_id', 'validation_result']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        # Create AI validation transaction
        from tokenomics.smart_contracts import TransactionType
        tx_data = {
            "validated_tx_id": data['transaction_id'],
            "validation_result": data['validation_result']
        }
        
        tx_id = tokenomics.create_transaction(
            TransactionType.AI_VALIDATION,
            data['validator_address'],
            data['validator_address'],
            Decimal("0"),
            tx_data
        )
        
        if tx_id:
            return jsonify({
                "success": True,
                "transaction_id": tx_id,
                "message": "AI validation completed successfully"
            })
        else:
            return jsonify({"error": "AI validation failed"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wallet_bp.route('/estimate_fee', methods=['POST'])
def estimate_fee():
    """Estimate transaction fee"""
    try:
        data = request.get_json()
        
        # Basic fee estimation
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        base_fee = tokenomics.config.transaction_fee
        
        # Adjust fee based on transaction type and amount
        tx_type = data.get('type', 'transfer')
        amount = Decimal(str(data.get('amount', 0)))
        
        if tx_type == 'stake':
            fee = base_fee * Decimal("2")  # Higher fee for staking
        elif tx_type == 'governance':
            fee = base_fee * Decimal("1.5")  # Higher fee for governance
        else:
            fee = base_fee
        
        # Add percentage-based fee for large amounts
        if amount > Decimal("10000"):
            fee += amount * Decimal("0.0001")  # 0.01% for large amounts
        
        return jsonify({
            "estimated_fee": str(fee),
            "base_fee": str(base_fee),
            "transaction_type": tx_type,
            "amount": str(amount)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

