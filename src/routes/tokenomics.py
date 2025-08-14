from flask import Blueprint, request, jsonify, current_app
from decimal import Decimal
import time

tokenomics_bp = Blueprint('tokenomics', __name__)

@tokenomics_bp.route('/stats', methods=['GET'])
def get_tokenomics_stats():
    """Get comprehensive tokenomics statistics"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        stats = tokenomics.get_tokenomics_stats()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/token_info', methods=['GET'])
def get_token_info():
    """Get token information"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        info = {
            "name": "NeuraX",
            "symbol": "NX",
            "decimals": 18,
            "total_supply": str(tokenomics.token_contract.total_supply),
            "circulating_supply": str(tokenomics.token_contract.circulating_supply),
            "burned_tokens": str(tokenomics.token_contract.burned_tokens),
            "contract_address": "NX_TOKEN_CONTRACT",
            "blockchain": "NeuraX",
            "consensus": "Proof of Intelligence",
            "features": [
                "AI-Powered Validation",
                "Quantum-Resistant Cryptography",
                "Zero-Knowledge Privacy",
                "Adaptive Governance",
                "Cross-Chain Compatibility"
            ]
        }
        
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/staking_info', methods=['GET'])
def get_staking_info():
    """Get staking information"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        info = {
            "total_staked": str(tokenomics.staking_contract.total_staked),
            "total_positions": len(tokenomics.staking_contract.staking_positions),
            "reward_pool": str(tokenomics.staking_contract.reward_pool),
            "base_apy": str(tokenomics.config.staking_reward_rate * 100),
            "min_stake": str(tokenomics.config.min_stake_amount),
            "max_stake": str(tokenomics.config.max_stake_amount),
            "unstaking_period": tokenomics.config.unstaking_period,
            "lock_periods": {
                "no_lock": {"multiplier": "1.0x", "apy": str(tokenomics.config.staking_reward_rate * 100)},
                "1_month": {"multiplier": "1.1x", "apy": str(tokenomics.config.staking_reward_rate * 110)},
                "6_months": {"multiplier": "1.25x", "apy": str(tokenomics.config.staking_reward_rate * 125)},
                "1_year": {"multiplier": "1.5x", "apy": str(tokenomics.config.staking_reward_rate * 150)}
            }
        }
        
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/governance_info', methods=['GET'])
def get_governance_info():
    """Get governance information"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        active_proposals = [
            p for p in tokenomics.governance_contract.proposals.values()
            if p["status"] == "pending"
        ]
        
        info = {
            "total_proposals": len(tokenomics.governance_contract.proposals),
            "active_proposals": len(active_proposals),
            "total_votes": len(tokenomics.governance_contract.votes),
            "reward_pool": str(tokenomics.governance_contract.reward_pool),
            "proposal_threshold": str(tokenomics.config.proposal_threshold),
            "voting_reward": str(tokenomics.config.voting_reward),
            "voting_periods": {
                "proposal_delay": "1 day",
                "voting_duration": "7 days",
                "execution_delay": "2 days"
            }
        }
        
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/proposals', methods=['GET'])
def get_proposals():
    """Get governance proposals"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 10)), 50)
        status = request.args.get('status')  # pending, passed, rejected
        
        # Filter proposals
        proposals = list(tokenomics.governance_contract.proposals.values())
        if status:
            proposals = [p for p in proposals if p["status"] == status]
        
        # Sort by creation time (newest first)
        proposals.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Paginate
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_proposals = proposals[start_idx:end_idx]
        
        # Add voting progress
        for proposal in paginated_proposals:
            total_votes = proposal["votes_for"] + proposal["votes_against"]
            if total_votes > 0:
                proposal["for_percentage"] = float(proposal["votes_for"] / total_votes * 100)
                proposal["against_percentage"] = float(proposal["votes_against"] / total_votes * 100)
            else:
                proposal["for_percentage"] = 0
                proposal["against_percentage"] = 0
            
            # Convert Decimal to string for JSON serialization
            proposal["votes_for"] = str(proposal["votes_for"])
            proposal["votes_against"] = str(proposal["votes_against"])
        
        return jsonify({
            "proposals": paginated_proposals,
            "total": len(proposals),
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/create_proposal', methods=['POST'])
def create_proposal():
    """Create a governance proposal"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['proposer', 'title', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        proposal_id = tokenomics.governance_contract.create_proposal(
            proposer=data['proposer'],
            title=data['title'],
            description=data['description'],
            proposal_data=data.get('proposal_data', {})
        )
        
        if proposal_id:
            return jsonify({
                "success": True,
                "proposal_id": proposal_id,
                "message": "Proposal created successfully"
            })
        else:
            return jsonify({"error": "Failed to create proposal"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/vote', methods=['POST'])
def vote_on_proposal():
    """Vote on a governance proposal"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['voter', 'proposal_id', 'vote_choice', 'voting_power']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        success = tokenomics.governance_contract.vote(
            voter=data['voter'],
            proposal_id=data['proposal_id'],
            vote_choice=data['vote_choice'],
            voting_power=Decimal(str(data['voting_power']))
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": "Vote cast successfully"
            })
        else:
            return jsonify({"error": "Failed to cast vote"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/ai_rewards_info', methods=['GET'])
def get_ai_rewards_info():
    """Get AI rewards information"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        info = {
            "reward_pool": str(tokenomics.ai_rewards_contract.reward_pool),
            "base_reward_rate": str(tokenomics.config.ai_validation_reward_rate),
            "total_validators": len(tokenomics.ai_rewards_contract.ai_scores),
            "average_ai_score": sum(tokenomics.ai_rewards_contract.ai_scores.values()) / max(1, len(tokenomics.ai_rewards_contract.ai_scores)),
            "validation_requirements": {
                "minimum_ai_score": 50,
                "accuracy_threshold": 0.6,
                "fraud_detection_bonus": "2x reward",
                "high_accuracy_bonus": "1.5x reward (>90% accuracy)"
            }
        }
        
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/validator_stats/<address>', methods=['GET'])
def get_validator_stats(address):
    """Get validator statistics"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        ai_score = tokenomics.ai_rewards_contract.ai_scores.get(address, 50.0)
        validation_history = tokenomics.ai_rewards_contract.validation_history.get(address, [])
        
        # Calculate statistics
        total_validations = len(validation_history)
        total_rewards = sum(Decimal(v['reward']) for v in validation_history)
        
        recent_validations = validation_history[-10:] if validation_history else []
        recent_accuracy = sum(v['validation_result'].get('accuracy', 0.5) for v in recent_validations) / max(1, len(recent_validations))
        
        stats = {
            "address": address,
            "ai_score": ai_score,
            "total_validations": total_validations,
            "total_rewards": str(total_rewards),
            "recent_accuracy": recent_accuracy,
            "validation_history": recent_validations,
            "rank": "Top 10%" if ai_score > 90 else "Top 25%" if ai_score > 75 else "Average"
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/liquidity_pools', methods=['GET'])
def get_liquidity_pools():
    """Get liquidity pools information"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        
        pools = []
        for pool_id, pool in tokenomics.liquidity_pools.items():
            pool_info = {
                "pool_id": pool_id,
                "token_a": pool.token_a,
                "token_b": pool.token_b,
                "reserve_a": str(pool.reserve_a),
                "reserve_b": str(pool.reserve_b),
                "total_liquidity": str(pool.total_liquidity),
                "fee_rate": str(pool.fee_rate * 100),  # Convert to percentage
                "providers": len(pool.liquidity_providers),
                "tvl": str(pool.reserve_a + pool.reserve_b)  # Simplified TVL
            }
            pools.append(pool_info)
        
        return jsonify({
            "pools": pools,
            "total_pools": len(pools)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/price_info', methods=['GET'])
def get_price_info():
    """Get token price information (simulated)"""
    try:
        # Simulate price data (in production, this would come from exchanges)
        import random
        
        base_price = 3.00  # $3.00 USD
        price_change = random.uniform(-0.1, 0.1)  # ±10% daily change
        current_price = base_price * (1 + price_change)
        
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        circulating_supply = float(tokenomics.token_contract.circulating_supply)
        market_cap = current_price * circulating_supply
        
        price_info = {
            "symbol": "NX",
            "price_usd": round(current_price, 4),
            "price_change_24h": round(price_change * 100, 2),
            "market_cap": round(market_cap, 2),
            "circulating_supply": circulating_supply,
            "volume_24h": round(market_cap * 0.1, 2),  # Simulated 10% of market cap
            "all_time_high": 5.50,
            "all_time_low": 0.50,
            "last_updated": time.time()
        }
        
        return jsonify(price_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tokenomics_bp.route('/distribution', methods=['GET'])
def get_token_distribution():
    """Get token distribution information"""
    try:
        tokenomics = current_app.config['NEURAX_TOKENOMICS']
        config = tokenomics.config
        
        distribution = {
            "total_supply": str(config.total_supply),
            "distribution": {
                "public_sale": {
                    "percentage": str(config.public_sale_percent),
                    "amount": str(config.total_supply * config.public_sale_percent / 100),
                    "description": "Public sale and initial distribution"
                },
                "team": {
                    "percentage": str(config.team_percent),
                    "amount": str(config.total_supply * config.team_percent / 100),
                    "description": "Team allocation with vesting"
                },
                "advisors": {
                    "percentage": str(config.advisors_percent),
                    "amount": str(config.total_supply * config.advisors_percent / 100),
                    "description": "Advisor allocation with vesting"
                },
                "ecosystem": {
                    "percentage": str(config.ecosystem_percent),
                    "amount": str(config.total_supply * config.ecosystem_percent / 100),
                    "description": "Ecosystem development and partnerships"
                },
                "treasury": {
                    "percentage": str(config.treasury_percent),
                    "amount": str(config.total_supply * config.treasury_percent / 100),
                    "description": "DAO treasury for governance"
                },
                "liquidity": {
                    "percentage": str(config.liquidity_percent),
                    "amount": str(config.total_supply * config.liquidity_percent / 100),
                    "description": "Liquidity provision and market making"
                }
            },
            "vesting_schedules": {
                "team": "4 year vesting with 1 year cliff",
                "advisors": "2 year vesting with 6 month cliff",
                "ecosystem": "Released based on milestones",
                "treasury": "Controlled by DAO governance"
            }
        }
        
        return jsonify(distribution)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

