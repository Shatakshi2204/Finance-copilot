"""
Chat Engine
===========
Orchestrates the chat flow with optimized response generation.
"""

import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

from model_loader import model_loader
from data_fetcher import data_fetcher, TriangulatedData, get_data
from config import app_config

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)


@dataclass
class ChatContext:
    """Context for chat generation."""
    country: Optional[str] = None
    metric: Optional[str] = None
    data: Optional[TriangulatedData] = None


class ChatEngine:
    """Handles chat orchestration and response generation."""
    
    def __init__(self):
        """Initialize chat engine."""
        self.history: list[ChatMessage] = []
        self.context = ChatContext()
    
    def _detect_intent(self, message: str) -> dict:
        """Detect user intent from message."""
        message_lower = message.lower()
        
        # Detect country
        country = None
        country_keywords = {
            "USA": ["usa", "united states", "america", "us economy", "american", "u.s."],
            "IND": ["india", "indian"],
            "EUU": ["eu", "european union", "europe", "eurozone", "euro area"],
            "CHN": ["china", "chinese"]
        }
        
        for code, keywords in country_keywords.items():
            if any(kw in message_lower for kw in keywords):
                country = code
                break
        
        # Detect metric
        metric = None
        metric_keywords = {
            "gdp_growth": ["gdp", "growth", "economic growth", "economy"],
            "inflation": ["inflation", "cpi", "prices", "cost of living"],
            "unemployment": ["unemployment", "jobless", "jobs", "employment", "labor"],
            "interest_rate": ["interest rate", "policy rate", "central bank", "rates", "fed"]
        }
        
        for metric_key, keywords in metric_keywords.items():
            if any(kw in message_lower for kw in keywords):
                metric = metric_key
                break
        
        # Default to USA and GDP if not specified
        if country is None and metric is not None:
            country = "USA"
        if metric is None and country is not None:
            metric = "gdp_growth"
        
        return {
            "country": country,
            "metric": metric,
            "is_data_request": country is not None or metric is not None
        }
    
    def _build_context_prompt(self, user_message: str, intent: dict) -> str:
        """Build prompt with live data context."""
        
        # If we have country and metric, fetch live data (cached)
        if intent["country"] and intent["metric"]:
            data = get_data(intent["metric"], intent["country"])
            self.context.data = data
            self.context.country = intent["country"]
            self.context.metric = intent["metric"]
            
            if data.consensus_value is not None:
                metric_name = app_config.metrics.get(data.metric, data.metric)
                return f"""DATA: {data.country} {metric_name}
- Value: {data.consensus_value:.2f}%
- FRED: {f'{data.fred_value:.2f}%' if data.fred_value else 'N/A'}
- World Bank: {f'{data.worldbank_value:.2f}%' if data.worldbank_value else 'N/A'}
- Confidence: {data.confidence.upper()}
- Period: {data.period}

QUESTION: {user_message}

Provide a brief, data-driven analysis. Cite the specific numbers above."""
        
        return user_message
    
    def generate_response(self, user_message: str) -> str:
        """Generate a response to the user message."""
        try:
            # Detect intent
            intent = self._detect_intent(user_message)
            
            # Build context-aware prompt
            prompt = self._build_context_prompt(user_message, intent)
            
            # Add to history
            self.history.append(ChatMessage(role="user", content=user_message))
            
            # Generate response
            response = model_loader.generate(prompt)
            
            # Clean up response
            response = response.strip()
            if not response:
                response = "I couldn't generate a response. Please try rephrasing your question."
            
            self.history.append(ChatMessage(
                role="assistant",
                content=response,
                metadata={"context": {
                    "country": self.context.country,
                    "metric": self.context.metric
                }}
            ))
            
            return response
            
        except Exception as e:
            logger.error(f"Chat generation error: {e}")
            return f"I encountered an error. Please try again. Error: {str(e)[:100]}"
    
    def get_current_data(self) -> Optional[TriangulatedData]:
        """Get the current context data."""
        return self.context.data
    
    def clear_history(self):
        """Clear chat history."""
        self.history = []
        self.context = ChatContext()
    
    def get_history(self) -> list[ChatMessage]:
        """Get chat history."""
        return self.history[-app_config.max_chat_history:]


# Global chat engine instance
chat_engine = ChatEngine()
