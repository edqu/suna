from typing import Dict, List, Optional, Set
from .ai_models import Model, ModelProvider, ModelCapability, ModelPricing, ModelConfig
from core.utils.config import config, EnvMode

# Check which API keys are available for default model selection
SHOULD_USE_GEMINI = (
    bool(config.GEMINI_API_KEY) and 
    len(config.GEMINI_API_KEY) > 10
)

SHOULD_USE_ANTHROPIC = (
    config.ENV_MODE == EnvMode.LOCAL and 
    bool(config.ANTHROPIC_API_KEY) and 
    len(config.ANTHROPIC_API_KEY) > 20 and  # Real keys are ~100+ chars
    config.ANTHROPIC_API_KEY.startswith("sk-ant-")  # Anthropic keys start with this
)

# Set default model IDs based on available API keys
# Priority: Gemini (free & fast) > Anthropic (local dev) > Bedrock (production)
if SHOULD_USE_GEMINI:
    FREE_MODEL_ID = "gemini/gemini-2.0-flash-exp"
    PREMIUM_MODEL_ID = "gemini/gemini-2.0-flash-exp"
    from core.utils.logger import logger
    logger.info(f"🤖 Using Google Gemini as default model (FREE, fast, capable)")
elif SHOULD_USE_ANTHROPIC:
    FREE_MODEL_ID = "anthropic/claude-haiku-4-5"
    PREMIUM_MODEL_ID = "anthropic/claude-haiku-4-5"
    from core.utils.logger import logger
    logger.info(f"🤖 Using Anthropic models as defaults (ENV_MODE={config.ENV_MODE.value}, ANTHROPIC_API_KEY configured)")
else:  
    FREE_MODEL_ID = "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/heol2zyy5v48"
    PREMIUM_MODEL_ID = "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/heol2zyy5v48"
    from core.utils.logger import logger
    logger.info(f"🤖 Using AWS Bedrock models as defaults (ENV_MODE={config.ENV_MODE.value})")

is_local = config.ENV_MODE == EnvMode.LOCAL

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, Model] = {}
        self._aliases: Dict[str, str] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        self.register(Model(
            id="anthropic/claude-haiku-4-5" if SHOULD_USE_ANTHROPIC else "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/heol2zyy5v48",
            name="Haiku 4.5",
            provider=ModelProvider.ANTHROPIC,
            aliases=["claude-haiku-4.5", "anthropic/claude-haiku-4.5", "Claude Haiku 4.5", "global.anthropic.claude-haiku-4-5-20251001-v1:0", "bedrock/global.anthropic.claude-haiku-4-5-20251001-v1:0", "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/heol2zyy5v48"],
            context_window=200_000,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.FUNCTION_CALLING,
                ModelCapability.VISION,
            ],
            pricing=ModelPricing(
                input_cost_per_million_tokens=1.00,
                output_cost_per_million_tokens=5.00
            ),
            tier_availability=["paid"],
            priority=102,
            recommended=True,
            enabled=True,
            config=ModelConfig()
        ))
        
        self.register(Model(
            id="anthropic/claude-sonnet-4-5-20250929" if SHOULD_USE_ANTHROPIC else "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/few7z4l830xh",
            name="Sonnet 4.5",
            provider=ModelProvider.ANTHROPIC,
            aliases=["claude-sonnet-4.5", "anthropic/claude-sonnet-4.5", "Claude Sonnet 4.5", "claude-sonnet-4-5-20250929", "global.anthropic.claude-sonnet-4-5-20250929-v1:0", "arn:aws:bedrock:us-west-2:935064898258:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0", "bedrock/global.anthropic.claude-sonnet-4-5-20250929-v1:0", "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/few7z4l830xh"],
            context_window=1_000_000,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.FUNCTION_CALLING,
                ModelCapability.VISION,
                ModelCapability.THINKING,
            ],
            pricing=ModelPricing(
                input_cost_per_million_tokens=3.00,
                output_cost_per_million_tokens=15.00
            ),
            tier_availability=["paid"],
            priority=101,
            recommended=True,
            enabled=True,
            config=ModelConfig(
                extra_headers={
                    "anthropic-beta": "context-1m-2025-08-07" 
                },
            )
        ))
        
        self.register(Model(
            id="anthropic/claude-sonnet-4-20250514" if SHOULD_USE_ANTHROPIC else "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/tyj1ks3nj9qf",
            name="Sonnet 4",
            provider=ModelProvider.ANTHROPIC,
            aliases=["claude-sonnet-4", "Claude Sonnet 4", "claude-sonnet-4-20250514", "global.anthropic.claude-sonnet-4-20250514-v1:0", "arn:aws:bedrock:us-west-2:935064898258:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0", "bedrock/global.anthropic.claude-sonnet-4-20250514-v1:0", "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/tyj1ks3nj9qf"],
            context_window=1_000_000,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.FUNCTION_CALLING,
                ModelCapability.VISION,
                ModelCapability.THINKING,
            ],
            pricing=ModelPricing(
                input_cost_per_million_tokens=3.00,
                output_cost_per_million_tokens=15.00
            ),
            tier_availability=["paid"],
            priority=100,
            recommended=True,
            enabled=True,
            config=ModelConfig(
                extra_headers={
                    "anthropic-beta": "context-1m-2025-08-07" 
                },
            )
        ))
        
        # Register direct Anthropic API models (always available if ANTHROPIC_API_KEY is set)
        if config.ANTHROPIC_API_KEY and len(config.ANTHROPIC_API_KEY) > 20:
            from core.utils.logger import logger
            logger.info("🔑 Registering direct Anthropic API models (claude-haiku-4.5, claude-sonnet-4.5, claude-sonnet-4, claude-opus-4, claude-3.5-sonnet)")
            # Haiku 4.5 - Direct Anthropic API
            self.register(Model(
                id="anthropic/claude-haiku-4-5-20251001",
                name="Haiku 4.5 (Direct)",
                provider=ModelProvider.ANTHROPIC,
                aliases=["claude-haiku-4.5-direct", "anthropic/claude-haiku-4.5-20251001"],
                context_window=200_000,
                capabilities=[
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.VISION,
                ],
                pricing=ModelPricing(
                    input_cost_per_million_tokens=1.00,
                    output_cost_per_million_tokens=5.00
                ),
                tier_availability=["free", "paid"],
                priority=102,
                recommended=True,
                enabled=True,
                config=ModelConfig()
            ))
            
            # Sonnet 4.5 - Direct Anthropic API
            self.register(Model(
                id="anthropic/claude-sonnet-4-5-20250929",
                name="Sonnet 4.5 (Direct)",
                provider=ModelProvider.ANTHROPIC,
                aliases=["claude-sonnet-4.5-direct"],
                context_window=1_000_000,
                capabilities=[
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.VISION,
                    ModelCapability.THINKING,
                ],
                pricing=ModelPricing(
                    input_cost_per_million_tokens=3.00,
                    output_cost_per_million_tokens=15.00
                ),
                tier_availability=["paid"],
                priority=101,
                recommended=True,
                enabled=True,
                config=ModelConfig(
                    extra_headers={
                        "anthropic-beta": "context-1m-2025-08-07" 
                    },
                )
            ))
            
            # Sonnet 4 - Direct Anthropic API
            self.register(Model(
                id="anthropic/claude-sonnet-4-20250514",
                name="Sonnet 4 (Direct)",
                provider=ModelProvider.ANTHROPIC,
                aliases=["claude-sonnet-4-direct"],
                context_window=1_000_000,
                capabilities=[
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.VISION,
                    ModelCapability.THINKING,
                ],
                pricing=ModelPricing(
                    input_cost_per_million_tokens=3.00,
                    output_cost_per_million_tokens=15.00
                ),
                tier_availability=["paid"],
                priority=100,
                recommended=True,
                enabled=True,
                config=ModelConfig(
                    extra_headers={
                        "anthropic-beta": "context-1m-2025-08-07" 
                    },
                )
            ))
            
            # Opus 4 - Direct Anthropic API (latest flagship)
            self.register(Model(
                id="anthropic/claude-opus-4-20250514",
                name="Opus 4",
                provider=ModelProvider.ANTHROPIC,
                aliases=["claude-opus-4", "opus-4", "Claude Opus 4"],
                context_window=1_000_000,
                capabilities=[
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.VISION,
                    ModelCapability.THINKING,
                ],
                pricing=ModelPricing(
                    input_cost_per_million_tokens=15.00,
                    output_cost_per_million_tokens=75.00
                ),
                tier_availability=["paid"],
                priority=103,
                recommended=False,
                enabled=True,
                config=ModelConfig(
                    extra_headers={
                        "anthropic-beta": "context-1m-2025-08-07" 
                    },
                )
            ))
            
            # Claude 3.5 Sonnet - Legacy but still popular
            self.register(Model(
                id="anthropic/claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                provider=ModelProvider.ANTHROPIC,
                aliases=["claude-3.5-sonnet", "claude-3-5-sonnet", "sonnet-3.5"],
                context_window=200_000,
                capabilities=[
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.VISION,
                ],
                pricing=ModelPricing(
                    input_cost_per_million_tokens=3.00,
                    output_cost_per_million_tokens=15.00
                ),
                tier_availability=["paid"],
                priority=90,
                recommended=False,
                enabled=True,
                config=ModelConfig()
            ))
        
        # Register Google Gemini models (always available if GEMINI_API_KEY is set)
        if config.GEMINI_API_KEY and len(config.GEMINI_API_KEY) > 10:
            from core.utils.logger import logger
            logger.info("🔑 Registering Google Gemini models (gemini-2.0-flash-exp)")
            
            # Gemini 2.0 Flash Experimental - Fast and capable
            self.register(Model(
                id="gemini/gemini-2.0-flash-exp",
                name="Gemini 2.0 Flash",
                provider=ModelProvider.GOOGLE,
                aliases=["gemini-2.0-flash", "gemini-2.0-flash-exp", "Gemini 2.0 Flash"],
                context_window=1_000_000,
                capabilities=[
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.VISION,
                ],
                pricing=ModelPricing(
                    input_cost_per_million_tokens=0.00,  # Free during experimental phase
                    output_cost_per_million_tokens=0.00
                ),
                tier_availability=["free", "paid"],
                priority=110,  # Highest priority for default
                recommended=True,
                enabled=True,
                config=ModelConfig()
            ))
            
            # Gemini 1.5 Flash - Reliable and fast
            self.register(Model(
                id="gemini/gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                provider=ModelProvider.GOOGLE,
                aliases=["gemini-1.5-flash", "Gemini 1.5 Flash"],
                context_window=1_000_000,
                capabilities=[
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.VISION,
                ],
                pricing=ModelPricing(
                    input_cost_per_million_tokens=0.075,
                    output_cost_per_million_tokens=0.30
                ),
                tier_availability=["free", "paid"],
                priority=95,
                recommended=False,
                enabled=True,
                config=ModelConfig()
            ))
            
            # Gemini 1.5 Pro - Most capable
            self.register(Model(
                id="gemini/gemini-1.5-pro",
                name="Gemini 1.5 Pro",
                provider=ModelProvider.GOOGLE,
                aliases=["gemini-1.5-pro", "Gemini 1.5 Pro"],
                context_window=2_000_000,
                capabilities=[
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.VISION,
                ],
                pricing=ModelPricing(
                    input_cost_per_million_tokens=1.25,
                    output_cost_per_million_tokens=5.00
                ),
                tier_availability=["paid"],
                priority=94,
                recommended=False,
                enabled=True,
                config=ModelConfig()
            ))
        
        # Register Ollama models (auto-discover from Ollama server)
        if config.OLLAMA_API_BASE:
            self._register_ollama_models()
        
        # Sonnet 3.7 - No global inference profile available yet
        # self.register(Model(
        #     id="anthropic/claude-3-7-sonnet-latest" if SHOULD_USE_ANTHROPIC else "global.anthropic.claude-3-7-sonnet-20250219-v1:0",
        #     name="Sonnet 3.7",
        #     provider=ModelProvider.ANTHROPIC,
        #     aliases=["claude-3.7", "Claude 3.7 Sonnet", "claude-3-7-sonnet-latest", "global.anthropic.claude-3-7-sonnet-20250219-v1:0", "arn:aws:bedrock:us-west-2:935064898258:inference-profile/global.anthropic.claude-3-7-sonnet-20250219-v1:0", "bedrock/global.anthropic.claude-3-7-sonnet-20250219-v1:0"],
        #     context_window=200_000,
        #     capabilities=[
        #         ModelCapability.CHAT,
        #         ModelCapability.FUNCTION_CALLING,
        #         ModelCapability.VISION,
        #     ],
        #     pricing=ModelPricing(
        #         input_cost_per_million_tokens=3.00,
        #         output_cost_per_million_tokens=15.00
        #     ),
        #     tier_availability=["paid"],
        #     priority=99,
        #     enabled=True,
        #     config=ModelConfig(
        #         # extra_headers={
        #         #     "anthropic-beta": "prompt-caching-2024-07-31"
        #         # },
        #     )
        # ))

        # Commented out non-Anthropic models as requested
        # self.register(Model(
        #     id="xai/grok-4-fast-non-reasoning",
        #     name="Grok 4 Fast",
        #     provider=ModelProvider.XAI,
        #     aliases=["grok-4-fast-non-reasoning", "Grok 4 Fast"],
        #     context_window=2_000_000,
        #     capabilities=[
        #         ModelCapability.CHAT,
        #         ModelCapability.FUNCTION_CALLING,
        #     ],
        #     pricing=ModelPricing(
        #         input_cost_per_million_tokens=0.20,
        #         output_cost_per_million_tokens=0.50
        #     ),
        #     tier_availability=["paid"],
        #     priority=98,
        #     enabled=True
        # ))        
        
        # self.register(Model(
        #     id="anthropic/claude-3-5-sonnet-latest",
        #     name="Claude 3.5 Sonnet",
        #     provider=ModelProvider.ANTHROPIC,
        #     aliases=["sonnet-3.5", "claude-3.5", "Claude 3.5 Sonnet", "claude-3-5-sonnet-latest"],
        #     context_window=200_000,
        #     capabilities=[
        #         ModelCapability.CHAT,
        #         ModelCapability.FUNCTION_CALLING,
        #         ModelCapability.VISION,
        #     ],
        #     pricing=ModelPricing(
        #         input_cost_per_million_tokens=3.00,
        #         output_cost_per_million_tokens=15.00
        #     ),
        #     tier_availability=["paid"],
        #     priority=90,
        #     enabled=True
        # ))
        
        # Commented out OpenAI models as requested
        # self.register(Model(
        #     id="openai/gpt-5",
        #     name="GPT-5",
        #     provider=ModelProvider.OPENAI,
        #     aliases=["gpt-5", "GPT-5"],
        #     context_window=400_000,
        #     capabilities=[
        #         ModelCapability.CHAT,
        #         ModelCapability.FUNCTION_CALLING,
        #         ModelCapability.VISION,
        #         ModelCapability.STRUCTURED_OUTPUT,
        #     ],
        #     pricing=ModelPricing(
        #         input_cost_per_million_tokens=1.25,
        #         output_cost_per_million_tokens=10.00
        #     ),
        #     tier_availability=["paid"],
        #     priority=97,
        #     enabled=True
        # ))
        
        # self.register(Model(
        #     id="openai/gpt-5-mini",
        #     name="GPT-5 Mini",
        #     provider=ModelProvider.OPENAI,
        #     aliases=["gpt-5-mini", "GPT-5 Mini"],
        #     context_window=400_000,
        #     capabilities=[
        #         ModelCapability.CHAT,
        #         ModelCapability.FUNCTION_CALLING,
        #         ModelCapability.STRUCTURED_OUTPUT,
        #     ],
        #     pricing=ModelPricing(
        #         input_cost_per_million_tokens=0.25,
        #         output_cost_per_million_tokens=2.00
        #     ),
        #     tier_availability=["free", "paid"],
        #     priority=96,
        #     enabled=True
        # ))
        
        # Commented out Google models as requested
        # self.register(Model(
        #     id="gemini/gemini-2.5-pro",
        #     name="Gemini 2.5 Pro",
        #     provider=ModelProvider.GOOGLE,
        #     aliases=["gemini-2.5-pro", "Gemini 2.5 Pro"],
        #     context_window=2_000_000,
        #     capabilities=[
        #         ModelCapability.CHAT,
        #         ModelCapability.FUNCTION_CALLING,
        #         ModelCapability.VISION,
        #         ModelCapability.STRUCTURED_OUTPUT,
        #     ],
        #     pricing=ModelPricing(
        #         input_cost_per_million_tokens=1.25,
        #         output_cost_per_million_tokens=10.00
        #     ),
        #     tier_availability=["paid"],
        #     priority=95,
        #     enabled=True
        # ))
        
        
        # self.register(Model(
        #     id="openrouter/moonshotai/kimi-k2",
        #     name="Kimi K2",
        #     provider=ModelProvider.MOONSHOTAI,
        #     aliases=["kimi-k2", "Kimi K2", "moonshotai/kimi-k2"],
        #     context_window=200_000,
        #     capabilities=[
        #         ModelCapability.CHAT,
        #         ModelCapability.FUNCTION_CALLING,
        #     ],
        #     pricing=ModelPricing(
        #         input_cost_per_million_tokens=1.00,
        #         output_cost_per_million_tokens=3.00
        #     ),
        #     tier_availability=["free", "paid"],
        #     priority=94,
        #     enabled=True,
        #     config=ModelConfig(
        #         extra_headers={
        #             "HTTP-Referer": config.OR_SITE_URL if hasattr(config, 'OR_SITE_URL') and config.OR_SITE_URL else "",
        #             "X-Title": config.OR_APP_NAME if hasattr(config, 'OR_APP_NAME') and config.OR_APP_NAME else ""
        #         }
        #     )
        # ))
        
        # # DeepSeek Models
        # self.register(Model(
        #     id="openrouter/deepseek/deepseek-chat",
        #     name="DeepSeek Chat",
        #     provider=ModelProvider.OPENROUTER,
        #     aliases=["deepseek", "deepseek-chat"],
        #     context_window=128_000,
        #     capabilities=[
        #         ModelCapability.CHAT, 
        #         ModelCapability.FUNCTION_CALLING
        #     ],
        #     pricing=ModelPricing(
        #         input_cost_per_million_tokens=0.38,
        #         output_cost_per_million_tokens=0.89
        #     ),
        #     tier_availability=["free", "paid"],
        #     priority=95,
        #     enabled=False  # Currently disabled
        # ))
        
        # # Qwen Models
        # self.register(Model(
        #     id="openrouter/qwen/qwen3-235b-a22b",
        #     name="Qwen3 235B",
        #     provider=ModelProvider.OPENROUTER,
        #     aliases=["qwen3", "qwen-3"],
        #     context_window=128_000,
        #     capabilities=[
        #         ModelCapability.CHAT, 
        #         ModelCapability.FUNCTION_CALLING
        #     ],
        #     pricing=ModelPricing(
        #         input_cost_per_million_tokens=0.13,
        #         output_cost_per_million_tokens=0.60
        #     ),
        #     tier_availability=["free", "paid"],
        #     priority=90,
        #     enabled=False  # Currently disabled
        # ))
        
        # Ollama Models (local deployment)
        self.register(Model(
            id="ollama/llama3:instruct",
            name="Llama 3 Instruct",
            provider=ModelProvider.OLLAMA,
            aliases=["llama3:instruct", "ollama_llama3_instruct"],
            context_window=8_192,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.FUNCTION_CALLING,
            ],
            pricing=ModelPricing(
                input_cost_per_million_tokens=0.00,
                output_cost_per_million_tokens=0.00
            ),
            tier_availability=["free", "paid"],
            priority=81,
            recommended=True,
            enabled=is_local,
            config=ModelConfig(
                api_base=getattr(config, 'OLLAMA_API_BASE', 'http://localhost:11434') if config else 'http://localhost:11434',
            )
        ))
        
        self.register(Model(
            id="ollama/llama3.3",
            name="Llama 3.3 70B",
            provider=ModelProvider.OLLAMA,
            aliases=["llama3.3", "ollama_llama3.3"],
            context_window=128_000,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.FUNCTION_CALLING,
            ],
            pricing=ModelPricing(
                input_cost_per_million_tokens=0.00,
                output_cost_per_million_tokens=0.00
            ),
            tier_availability=["free", "paid"],
            priority=80,
            enabled=is_local,
            config=ModelConfig(
                api_base=getattr(config, 'OLLAMA_API_BASE', 'http://localhost:11434') if config else 'http://localhost:11434',
            )
        ))
        
        self.register(Model(
            id="ollama/qwen2.5-coder",
            name="Qwen 2.5 Coder",
            provider=ModelProvider.OLLAMA,
            aliases=["qwen2.5-coder", "ollama_qwen2.5-coder"],
            context_window=32_768,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.FUNCTION_CALLING,
            ],
            pricing=ModelPricing(
                input_cost_per_million_tokens=0.00,
                output_cost_per_million_tokens=0.00
            ),
            tier_availability=["free", "paid"],
            priority=79,
            enabled=is_local,
            config=ModelConfig(
                api_base=getattr(config, 'OLLAMA_API_BASE', 'http://localhost:11434') if config else 'http://localhost:11434',
            )
        ))
        
        self.register(Model(
            id="ollama/deepseek-r1:70b",
            name="DeepSeek R1 70B",
            provider=ModelProvider.OLLAMA,
            aliases=["deepseek-r1:70b", "ollama_deepseek-r1"],
            context_window=64_000,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.FUNCTION_CALLING,
            ],
            pricing=ModelPricing(
                input_cost_per_million_tokens=0.00,
                output_cost_per_million_tokens=0.00
            ),
            tier_availability=["free", "paid"],
            priority=78,
            enabled=is_local,
            config=ModelConfig(
                api_base=getattr(config, 'OLLAMA_API_BASE', 'http://localhost:11434') if config else 'http://localhost:11434',
            )
        ))
        
        
        
    
    def register(self, model: Model) -> None:
        self._models[model.id] = model
        # Register both exact ID and lowercase version for case-insensitive lookup
        self._aliases[model.id.lower()] = model.id
        for alias in model.aliases:
            self._aliases[alias.lower()] = model.id
    
    def _register_ollama_models(self) -> None:
        """Auto-discover and register models from Ollama server."""
        try:
            import requests
            from core.utils.logger import logger
            
            ollama_base = config.OLLAMA_API_BASE
            
            # Fetch models from Ollama (synchronous)
            try:
                response = requests.get(f"{ollama_base}/api/tags", timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                else:
                    logger.debug(f"Ollama server returned status {response.status_code}")
                    data = None
            except Exception as e:
                logger.debug(f"Could not connect to Ollama server at {ollama_base}: {e}")
                data = None
            
            if not data:
                logger.info(f"🔧 Ollama server not available at {config.OLLAMA_API_BASE}, skipping auto-registration")
                return
            
            models_data = data.get("models", [])
            
            if not models_data:
                logger.info(f"🔧 No models found in Ollama - run 'ollama pull <model>' to add models")
                return
            
            logger.info(f"🔑 Auto-registering {len(models_data)} Ollama models from {config.OLLAMA_API_BASE}")
            
            # Known model metadata for better configuration
            vision_models = ["llava", "qwen", "qwen2-vl", "qwen3-vl", "bakllava", "moondream", "vision", "llama3.2-vision"]
            large_context_models = ["qwen", "llama3", "gemma2", "mixtral", "llama3.2"]
            
            for model_data in models_data:
                model_name = model_data.get("name", "")
                if not model_name:
                    continue
                
                # Parse model info
                model_base = model_name.split(":")[0] if ":" in model_name else model_name
                model_display_name = model_base.replace("-", " ").title()
                
                # Determine capabilities based on model name
                capabilities = [ModelCapability.CHAT]
                
                # Check for vision capability
                if any(vm in model_name.lower() for vm in vision_models):
                    capabilities.append(ModelCapability.VISION)
                
                # Most modern Ollama models support function calling
                capabilities.append(ModelCapability.FUNCTION_CALLING)
                
                # Determine context window
                context_window = 4_096  # Conservative default
                if any(lc in model_name.lower() for lc in large_context_models):
                    context_window = 128_000
                
                # Determine if recommended
                recommended = "qwen3-vl" in model_name.lower() or "llama3" in model_name.lower()
                
                # Calculate priority (higher for vision models)
                priority = 105 if ModelCapability.VISION in capabilities else 85
                
                # Register the model
                self.register(Model(
                    id=f"ollama/{model_name}",
                    name=f"{model_display_name} (Local)",
                    provider=ModelProvider.OLLAMA,
                    aliases=[model_name, model_base, f"ollama/{model_base}"],
                    context_window=context_window,
                    capabilities=capabilities,
                    pricing=ModelPricing(
                        input_cost_per_million_tokens=0.00,
                        output_cost_per_million_tokens=0.00
                    ),
                    tier_availability=["free", "paid"],
                    priority=priority,
                    recommended=recommended,
                    enabled=True,
                    config=ModelConfig(
                        api_base=config.OLLAMA_API_BASE
                    )
                ))
                
                logger.debug(f"  ✓ Registered: {model_name} (vision={ModelCapability.VISION in capabilities})")
            
            logger.info(f"✅ Successfully registered {len(models_data)} Ollama models")
            
        except Exception as e:
            from core.utils.logger import logger
            logger.warning(f"Failed to auto-register Ollama models: {e}")
    
    def get(self, model_id: str) -> Optional[Model]:
        # Handle None or empty model_id
        if not model_id:
            return None
        
        # Try exact match first
        if model_id in self._models:
            return self._models[model_id]
        
        # Try case-insensitive lookup
        model_id_lower = model_id.lower()
        if model_id_lower in self._aliases:
            actual_id = self._aliases[model_id_lower]
            return self._models.get(actual_id)
        
        return None
    
    def get_all(self, enabled_only: bool = True) -> List[Model]:
        models = list(self._models.values())
        if enabled_only:
            models = [m for m in models if m.enabled]
        return models
    
    def get_by_tier(self, tier: str, enabled_only: bool = True) -> List[Model]:
        models = self.get_all(enabled_only)
        return [m for m in models if tier in m.tier_availability]
    
    def get_by_provider(self, provider: ModelProvider, enabled_only: bool = True) -> List[Model]:
        models = self.get_all(enabled_only)
        return [m for m in models if m.provider == provider]
    
    def get_by_capability(self, capability: ModelCapability, enabled_only: bool = True) -> List[Model]:
        models = self.get_all(enabled_only)
        return [m for m in models if capability in m.capabilities]
    
    def resolve_model_id(self, model_id: str) -> Optional[str]:
        model = self.get(model_id)
        return model.id if model else None
    
    
    def get_aliases(self, model_id: str) -> List[str]:
        model = self.get(model_id)
        return model.aliases if model else []
    
    def enable_model(self, model_id: str) -> bool:
        model = self.get(model_id)
        if model:
            model.enabled = True
            return True
        return False
    
    def disable_model(self, model_id: str) -> bool:
        model = self.get(model_id)
        if model:
            model.enabled = False
            return True
        return False
    
    def get_context_window(self, model_id: str, default: int = 31_000) -> int:
        model = self.get(model_id)
        return model.context_window if model else default
    
    def get_pricing(self, model_id: str) -> Optional[ModelPricing]:
        model = self.get(model_id)
        return model.pricing if model else None
    
    def to_legacy_format(self) -> Dict:
        models_dict = {}
        pricing_dict = {}
        context_windows_dict = {}
        
        for model in self.get_all(enabled_only=True):
            models_dict[model.id] = {
                "pricing": {
                    "input_cost_per_million_tokens": model.pricing.input_cost_per_million_tokens,
                    "output_cost_per_million_tokens": model.pricing.output_cost_per_million_tokens,
                } if model.pricing else None,
                "context_window": model.context_window,
                "tier_availability": model.tier_availability,
            }
            
            if model.pricing:
                pricing_dict[model.id] = {
                    "input_cost_per_million_tokens": model.pricing.input_cost_per_million_tokens,
                    "output_cost_per_million_tokens": model.pricing.output_cost_per_million_tokens,
                }
            
            context_windows_dict[model.id] = model.context_window
        
        free_models = [m.id for m in self.get_by_tier("free")]
        paid_models = [m.id for m in self.get_by_tier("paid")]
        
        # Debug logging
        from core.utils.logger import logger
        logger.debug(f"Legacy format generation: {len(free_models)} free models, {len(paid_models)} paid models")
        logger.debug(f"Free models: {free_models}")
        logger.debug(f"Paid models: {paid_models}")
        
        return {
            "MODELS": models_dict,
            "HARDCODED_MODEL_PRICES": pricing_dict,
            "MODEL_CONTEXT_WINDOWS": context_windows_dict,
            "FREE_TIER_MODELS": free_models,
            "PAID_TIER_MODELS": paid_models,
        }

registry = ModelRegistry() 