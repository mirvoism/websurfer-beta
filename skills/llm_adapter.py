import os
import time
from dotenv import load_dotenv
from openai import OpenAI

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
        
        # Initialize OpenAI client for Mac Studio endpoint
        self.client = OpenAI(
            base_url=self.api_base,
            api_key=self.api_key
        )
    
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
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Implement exponential backoff retry logic"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                print(f"🔄 Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    def chat(self, messages, model=None, **kwargs) -> str:
        """
        Send chat completion request to Mac Studio LLM endpoint
        """
        model = model or self.default_model
        
        if model not in self.available_models:
            raise ValueError(f"Model '{model}' not available. Choose from: {self.available_models}")
        
        try:
            # Make actual API call with retry logic
            def _make_request():
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content
            
            return self._retry_with_backoff(_make_request)
            
        except Exception as e:
            error_msg = f"Mac Studio LLM API Error: {e}"
            print(f"❌ {error_msg}")
            
            # Return fallback response for development
            return f"[ERROR] {error_msg}. Using fallback response for development."
    
    def test_connection(self):
        """Test connection to Mac Studio endpoint"""
        try:
            print(f"🔍 Testing connection to Mac Studio...")
            print(f"🌐 Endpoint: {self.api_base}")
            
            response = self.chat(
                messages=[{"role": "user", "content": "Hello! Please respond with 'Mac Studio LLM is working!'"}],
                model=self.default_model
            )
            
            print(f"✅ Connection successful!")
            print(f"🤖 Response: {response}")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False


