import os
from dotenv import load_dotenv

class LLM:
    def __init__(self, provider="mac_studio"):
        # Load environment variables
        load_dotenv()
        
        self.provider = provider
        self.api_base = os.getenv('OPENAI_API_BASE', 'https://matiass-mac-studio.tail174e9b.ts.net/v1')
        self.api_key = os.getenv('OPENAI_API_KEY', 'ollama')
        self.default_model = os.getenv('DEFAULT_MODEL', 'deepseek-r1')
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        # Available models on Mac Studio
        self.available_models = [
            'deepseek-r1',
            'qwen3:32b', 
            'qwen25',
            'llama4:scout',
            'llama4:maverick'
        ]
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that configuration is properly set"""
        if not self.api_base:
            raise ValueError("OPENAI_API_BASE environment variable is required")
        
        if self.default_model not in self.available_models:
            print(f"Warning: DEFAULT_MODEL '{self.default_model}' not in available models: {self.available_models}")
            print(f"Using fallback model: deepseek-r1")
            self.default_model = 'deepseek-r1'
    
    def get_config(self):
        """Return current configuration for debugging"""
        return {
            'provider': self.provider,
            'api_base': self.api_base,
            'default_model': self.default_model,
            'available_models': self.available_models,
            'max_retries': self.max_retries
        }

    def chat(self, messages, model=None, **kwargs) -> str:
        """
        Chat method - will be implemented with actual Mac Studio integration in Task 4
        For now, returns configuration-aware dummy response
        """
        model = model or self.default_model
        
        if model not in self.available_models:
            raise ValueError(f"Model '{model}' not available. Choose from: {self.available_models}")
        
        # Placeholder response with config info
        return f"[Mac Studio {model}] Configuration loaded successfully. Ready for Task 4 implementation."


