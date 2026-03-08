"""
ProtoForge Credit System
Each prompt deducts a small amount (pennies), first prompt is free
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Credit costs per prompt (in USD)
CREDIT_COSTS = {
    'software': 0.01,    # 1 cent
    'hardware': 0.02,    # 2 cents (more complex)
    'hybrid': 0.03,      # 3 cents (most complex)
}

# Free tier allocation
FREE_TIER_PROMPTS = 1   # First prompt free


class CreditSystem:
    """Manage user credits and deposits"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / "credits.json"
        self._load_users()
    
    def _load_users(self):
        """Load users from file"""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            self.users = {}
    
    def _save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def get_balance(self, user_id: str) -> Dict[str, Any]:
        """Get user's credit balance"""
        if user_id not in self.users:
            # New user gets free tier
            self.users[user_id] = {
                'balance': 0.0,
                'deposited': 0.0,
                'prompts_used': 0,
                'prompts_free': FREE_TIER_PROMPTS,
                'created_at': datetime.utcnow().isoformat()
            }
            self._save_users()
        
        return self.users[user_id]
    
    def deposit(self, user_id: str, amount: float) -> Dict[str, Any]:
        """Add credits to user's account"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        user = self.get_balance(user_id)
        user['balance'] += amount
        user['deposited'] += amount
        user['last_deposit'] = datetime.utcnow().isoformat()
        user['last_deposit_amount'] = amount
        self._save_users()
        
        return {
            'success': True,
            'new_balance': user['balance'],
            'amount_added': amount
        }
    
    def get_cost(self, mode: str) -> float:
        """Get cost for a prompt"""
        return CREDIT_COSTS.get(mode, 0.01)
    
    def can_prompt(self, user_id: str, mode: str) -> tuple[bool, str]:
        """Check if user can make a prompt"""
        user = self.get_balance(user_id)
        
        # Check free prompts
        if user.get('prompts_free', 0) > 0:
            return True, "free"
        
        # Check balance
        cost = self.get_cost(mode)
        if user['balance'] >= cost:
            return True, "paid"
        
        return False, f"Insufficient credits. Need ${cost:.2f}, have ${user['balance']:.2f}. Deposit more to continue."
    
    def use_prompt(self, user_id: str, mode: str) -> Dict[str, Any]:
        """Use a prompt and deduct credits"""
        user = self.get_balance(user_id)
        
        # Check free prompts first
        if user.get('prompts_free', 0) > 0:
            user['prompts_free'] -= 1
            user['prompts_used'] += 1
            self._save_users()
            
            return {
                'success': True,
                'type': 'free',
                'remaining_free': user['prompts_free'],
                'cost': 0.0,
                'new_balance': user['balance']
            }
        
        # Deduct from balance
        cost = self.get_cost(mode)
        
        if user['balance'] < cost:
            raise ValueError(f"Insufficient credits. Need ${cost:.2f}, have ${user['balance']:.2f}")
        
        user['balance'] -= cost
        user['prompts_used'] += 1
        self._save_users()
        
        return {
            'success': True,
            'type': 'paid',
            'cost': cost,
            'new_balance': user['balance'],
            'prompts_used': user['prompts_used']
        }
    
    def get_history(self, user_id: str, limit: int = 10) -> list:
        """Get user's transaction history"""
        # Could extend to store transaction history
        user = self.get_balance(user_id)
        return [
            {
                'prompts_used': user.get('prompts_used', 0),
                'total_deposited': user.get('deposited', 0),
                'current_balance': user['balance'],
                'free_prompts_remaining': user.get('prompts_free', 0)
            }
        ]
