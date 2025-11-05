"""
Embedding Models Registry

Manages embedding models for semantic search, RAG, and knowledge base operations.
Supports multiple providers: OpenAI, Sentence Transformers (local), Ollama (local), etc.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from core.utils.config import config
from core.utils.logger import logger


class EmbeddingProvider(Enum):
    OPENAI = "openai"
    SENTENCE_TRANSFORMERS = "sentence_transformers"  # Local, free
    OLLAMA = "ollama"  # Local, free
    GOOGLE = "google"  # Gemini embeddings
    COHERE = "cohere"
    VOYAGE = "voyage"


@dataclass
class EmbeddingPricing:
    cost_per_million_tokens: float
    
    @property
    def cost_per_token(self) -> float:
        return self.cost_per_million_tokens / 1_000_000


@dataclass
class EmbeddingModel:
    """Represents an embedding model configuration."""
    id: str
    name: str
    provider: EmbeddingProvider
    dimensions: int
    max_input_tokens: int
    pricing: EmbeddingPricing
    
    # Model metadata
    aliases: List[str]
    enabled: bool = True
    recommended: bool = False
    priority: int = 50
    
    # Availability
    tier_availability: List[str] = None  # ["free", "paid"]
    requires_api_key: bool = True
    is_local: bool = False  # Runs locally (no API costs)
    
    # Technical details
    api_base: Optional[str] = None
    model_name_in_api: Optional[str] = None  # If different from id
    
    def __post_init__(self):
        if self.tier_availability is None:
            self.tier_availability = ["free", "paid"] if self.is_local else ["paid"]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider.value,
            "dimensions": self.dimensions,
            "max_input_tokens": self.max_input_tokens,
            "pricing": {
                "cost_per_million_tokens": self.pricing.cost_per_million_tokens
            },
            "aliases": self.aliases,
            "enabled": self.enabled,
            "recommended": self.recommended,
            "priority": self.priority,
            "tier_availability": self.tier_availability,
            "is_local": self.is_local,
            "requires_api_key": self.requires_api_key
        }


class EmbeddingModelRegistry:
    """Registry for embedding models."""
    
    def __init__(self):
        self._models: Dict[str, EmbeddingModel] = {}
        self._aliases: Dict[str, str] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Register all available embedding models."""
        
        # OpenAI Embeddings (if API key available)
        if config.OPENAI_API_KEY and len(config.OPENAI_API_KEY) > 20:
            logger.info("🔑 Registering OpenAI embedding models")
            
            # text-embedding-3-small (best value)
            self.register(EmbeddingModel(
                id="openai/text-embedding-3-small",
                name="OpenAI Embedding Small",
                provider=EmbeddingProvider.OPENAI,
                dimensions=1536,
                max_input_tokens=8191,
                pricing=EmbeddingPricing(cost_per_million_tokens=0.02),
                aliases=["text-embedding-3-small", "embedding-small", "openai-small"],
                recommended=True,
                priority=100,
                tier_availability=["free", "paid"],
                requires_api_key=True,
                is_local=False
            ))
            
            # text-embedding-3-large (most capable)
            self.register(EmbeddingModel(
                id="openai/text-embedding-3-large",
                name="OpenAI Embedding Large",
                provider=EmbeddingProvider.OPENAI,
                dimensions=3072,
                max_input_tokens=8191,
                pricing=EmbeddingPricing(cost_per_million_tokens=0.13),
                aliases=["text-embedding-3-large", "embedding-large", "openai-large"],
                recommended=False,
                priority=95,
                tier_availability=["paid"],
                requires_api_key=True,
                is_local=False
            ))
            
            # Ada v2 (legacy but still supported)
            self.register(EmbeddingModel(
                id="openai/text-embedding-ada-002",
                name="OpenAI Ada v2",
                provider=EmbeddingProvider.OPENAI,
                dimensions=1536,
                max_input_tokens=8191,
                pricing=EmbeddingPricing(cost_per_million_tokens=0.10),
                aliases=["text-embedding-ada-002", "ada-002"],
                recommended=False,
                priority=80,
                tier_availability=["paid"],
                requires_api_key=True,
                is_local=False
            ))
        
        # Google Gemini Embeddings (if API key available)
        if config.GEMINI_API_KEY and len(config.GEMINI_API_KEY) > 10:
            logger.info("🔑 Registering Google Gemini embedding models")
            
            self.register(EmbeddingModel(
                id="google/text-embedding-004",
                name="Gemini Text Embedding",
                provider=EmbeddingProvider.GOOGLE,
                dimensions=768,
                max_input_tokens=2048,
                pricing=EmbeddingPricing(cost_per_million_tokens=0.00),  # FREE
                aliases=["text-embedding-004", "gemini-embedding"],
                recommended=True,
                priority=110,  # Highest priority (free!)
                tier_availability=["free", "paid"],
                requires_api_key=True,
                is_local=False
            ))
        
        # Ollama Embeddings (if Ollama configured - auto-discover)
        if config.OLLAMA_API_BASE:
            self._register_ollama_embedding_models()
        
        # Sentence Transformers (local, always available)
        logger.info("🔑 Registering local Sentence Transformers embedding models")
        
        # all-MiniLM-L6-v2 (fastest, smallest)
        self.register(EmbeddingModel(
            id="sentence-transformers/all-MiniLM-L6-v2",
            name="MiniLM L6 (Local)",
            provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
            dimensions=384,
            max_input_tokens=256,
            pricing=EmbeddingPricing(cost_per_million_tokens=0.00),  # FREE
            aliases=["all-MiniLM-L6-v2", "minilm", "local-small"],
            recommended=True,
            priority=105,
            tier_availability=["free", "paid"],
            requires_api_key=False,
            is_local=True
        ))
        
        # all-mpnet-base-v2 (better quality)
        self.register(EmbeddingModel(
            id="sentence-transformers/all-mpnet-base-v2",
            name="MPNet Base (Local)",
            provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
            dimensions=768,
            max_input_tokens=384,
            pricing=EmbeddingPricing(cost_per_million_tokens=0.00),  # FREE
            aliases=["all-mpnet-base-v2", "mpnet", "local-medium"],
            recommended=False,
            priority=90,
            tier_availability=["free", "paid"],
            requires_api_key=False,
            is_local=True
        ))
        
        # multi-qa-mpnet-base-dot-v1 (optimized for Q&A)
        self.register(EmbeddingModel(
            id="sentence-transformers/multi-qa-mpnet-base-dot-v1",
            name="Multi-QA MPNet (Local)",
            provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
            dimensions=768,
            max_input_tokens=512,
            pricing=EmbeddingPricing(cost_per_million_tokens=0.00),  # FREE
            aliases=["multi-qa-mpnet-base-dot-v1", "qa-mpnet"],
            recommended=False,
            priority=85,
            tier_availability=["free", "paid"],
            requires_api_key=False,
            is_local=True
        ))
    
    def _register_ollama_embedding_models(self) -> None:
        """Auto-discover Ollama embedding models."""
        try:
            import requests
            
            ollama_base = config.OLLAMA_API_BASE
            
            # Fetch models from Ollama
            try:
                response = requests.get(f"{ollama_base}/api/tags", timeout=2.0)
                if response.status_code != 200:
                    logger.debug(f"Ollama server returned status {response.status_code}")
                    return
                data = response.json()
            except Exception as e:
                logger.debug(f"Could not connect to Ollama for embeddings: {e}")
                return
            
            models_data = data.get("models", [])
            if not models_data:
                return
            
            # Known embedding models in Ollama
            embedding_model_patterns = ["nomic-embed", "mxbai-embed", "all-minilm", "bge"]
            
            embedding_models_found = []
            for model_data in models_data:
                model_name = model_data.get("name", "")
                if not model_name:
                    continue
                
                # Check if it's an embedding model
                is_embedding = any(pattern in model_name.lower() for pattern in embedding_model_patterns)
                if not is_embedding:
                    continue
                
                embedding_models_found.append(model_name)
                
                # Parse model info
                model_base = model_name.split(":")[0] if ":" in model_name else model_name
                model_display_name = model_base.replace("-", " ").title()
                
                # Determine dimensions (common sizes, can be overridden)
                dimensions = 768  # Common default
                if "nomic" in model_name.lower():
                    dimensions = 768
                elif "mxbai" in model_name.lower():
                    dimensions = 1024
                elif "bge" in model_name.lower():
                    dimensions = 1024
                
                # Register the embedding model
                self.register(EmbeddingModel(
                    id=f"ollama/{model_name}",
                    name=f"{model_display_name} (Local)",
                    provider=EmbeddingProvider.OLLAMA,
                    dimensions=dimensions,
                    max_input_tokens=512,
                    pricing=EmbeddingPricing(cost_per_million_tokens=0.00),
                    aliases=[model_name, model_base, f"ollama/{model_base}"],
                    recommended="nomic" in model_name.lower(),
                    priority=108,  # High priority for local
                    tier_availability=["free", "paid"],
                    requires_api_key=False,
                    is_local=True,
                    api_base=config.OLLAMA_API_BASE
                ))
                
                logger.debug(f"  ✓ Registered embedding: {model_name}")
            
            if embedding_models_found:
                logger.info(f"✅ Registered {len(embedding_models_found)} Ollama embedding models: {', '.join(embedding_models_found)}")
            
        except Exception as e:
            logger.warning(f"Failed to auto-register Ollama embedding models: {e}")
    
    def register(self, model: EmbeddingModel) -> None:
        """Register an embedding model."""
        self._models[model.id] = model
        self._aliases[model.id.lower()] = model.id
        for alias in model.aliases:
            self._aliases[alias.lower()] = model.id
    
    def get(self, model_id: str) -> Optional[EmbeddingModel]:
        """Get embedding model by ID or alias."""
        if not model_id:
            return None
        
        # Try exact match
        if model_id in self._models:
            return self._models[model_id]
        
        # Try case-insensitive lookup
        model_id_lower = model_id.lower()
        if model_id_lower in self._aliases:
            actual_id = self._aliases[model_id_lower]
            return self._models.get(actual_id)
        
        return None
    
    def get_all(self, enabled_only: bool = True) -> List[EmbeddingModel]:
        """Get all embedding models."""
        models = list(self._models.values())
        if enabled_only:
            models = [m for m in models if m.enabled]
        return models
    
    def get_by_provider(self, provider: EmbeddingProvider, enabled_only: bool = True) -> List[EmbeddingModel]:
        """Get embedding models by provider."""
        models = self.get_all(enabled_only)
        return [m for m in models if m.provider == provider]
    
    def get_free_models(self, enabled_only: bool = True) -> List[EmbeddingModel]:
        """Get all free embedding models (local + free cloud)."""
        models = self.get_all(enabled_only)
        return [m for m in models if m.pricing.cost_per_million_tokens == 0.00]
    
    def get_default_model(self) -> Optional[EmbeddingModel]:
        """
        Get the default embedding model based on availability and cost.
        
        Priority:
        1. Free cloud models (Gemini)
        2. Local models (Sentence Transformers/Ollama)
        3. Paid cloud models (OpenAI)
        """
        models = self.get_all(enabled_only=True)
        if not models:
            return None
        
        # Sort by priority (highest first)
        models.sort(key=lambda m: m.priority, reverse=True)
        
        # Return highest priority model
        return models[0]
    
    def get_recommended_models(self) -> List[EmbeddingModel]:
        """Get recommended embedding models."""
        models = self.get_all(enabled_only=True)
        return [m for m in models if m.recommended]


# Global registry instance
embedding_registry = EmbeddingModelRegistry()


def get_embedding_model(model_id: Optional[str] = None) -> EmbeddingModel:
    """
    Get embedding model by ID, or return default if not specified.
    
    Args:
        model_id: Model ID or alias (optional)
        
    Returns:
        EmbeddingModel instance
        
    Raises:
        ValueError: If model not found and no default available
    """
    if model_id:
        model = embedding_registry.get(model_id)
        if model:
            return model
        logger.warning(f"Embedding model '{model_id}' not found, using default")
    
    # Get default model
    default = embedding_registry.get_default_model()
    if not default:
        raise ValueError("No embedding models available. Configure at least one embedding provider.")
    
    return default


def get_embedding_params(model_id: Optional[str] = None) -> Dict:
    """
    Get parameters for making embedding API calls.
    
    Args:
        model_id: Model ID or alias (optional, uses default if not specified)
        
    Returns:
        Dict with model, provider, dimensions, api_base, etc.
    """
    model = get_embedding_model(model_id)
    
    params = {
        "model": model.model_name_in_api or model.id,
        "provider": model.provider.value,
        "dimensions": model.dimensions,
        "max_input_tokens": model.max_input_tokens,
        "is_local": model.is_local
    }
    
    if model.api_base:
        params["api_base"] = model.api_base
    
    return params
