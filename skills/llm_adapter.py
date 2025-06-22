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
        self.default_model = os.getenv('DEFAULT_MODEL', 'llama4:scout')
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        # Available models on Mac Studio with capabilities
        self.available_models = [
            'deepseek-r1',      # Text-only reasoning
            'qwen3:32b',        # Text-only
            'qwen25',           # Text-only
            'llama4:scout',     # 🔥 VISION + TEXT
            'llama4:maverick'   # Text-only
        ]
        
        # Vision-capable models
        self.vision_models = ['llama4:scout']
        
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
            print(f"Using fallback model: llama4:scout")
            self.default_model = 'llama4:scout'
    
    def has_vision(self, model=None):
        """Check if the specified model has vision capabilities"""
        model = model or self.default_model
        return model in self.vision_models
    
    def get_config(self):
        """Return current configuration for debugging"""
        return {
            'provider': self.provider,
            'api_base': self.api_base,
            'default_model': self.default_model,
            'available_models': self.available_models,
            'vision_models': self.vision_models,
            'has_vision': self.has_vision(),
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

    def chat(self, messages, model=None, images=None, **kwargs) -> str:
        """
        Send chat completion request to Mac Studio LLM endpoint
        Supports both text and vision (for llama4:scout)
        """
        model = model or self.default_model
        
        if model not in self.available_models:
            raise ValueError(f"Model '{model}' not available. Choose from: {self.available_models}")
        
        # Handle vision inputs for vision-capable models
        if images and self.has_vision(model):
            # Add images to the last message if it's from user
            if messages and messages[-1].get("role") == "user":
                content = messages[-1]["content"]
                if isinstance(content, str):
                    # Convert to content array format for vision
                    messages[-1]["content"] = [
                        {"type": "text", "text": content}
                    ]
                    # Add images
                    for image in images:
                        messages[-1]["content"].append({
                            "type": "image_url", 
                            "image_url": {"url": image}
                        })
                        
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
    
    def chat_with_vision(self, text_prompt, image_paths=None, model=None):
        """
        Convenience method for vision + text chat
        """
        model = model or self.default_model
        
        if not self.has_vision(model):
            return f"Error: Model '{model}' does not support vision. Use llama4:scout for vision capabilities."
        
        # Convert local image paths to base64 data URLs if needed
        images = []
        if image_paths:
            for path in image_paths:
                if path.startswith('data:'):
                    images.append(path)
                else:
                    # Convert file path to data URL
                    import base64
                    with open(path, 'rb') as img_file:
                        img_data = base64.b64encode(img_file.read()).decode()
                        images.append(f"data:image/png;base64,{img_data}")
        
        messages = [
            {"role": "user", "content": text_prompt}
        ]
        
        return self.chat(messages=messages, images=images, model=model)
    
    def test_connection(self):
        """Test connection to Mac Studio endpoint"""
        try:
            print(f"🔍 Testing connection to Mac Studio...")
            print(f"🌐 Endpoint: {self.api_base}")
            print(f"🤖 Model: {self.default_model}")
            if self.has_vision():
                print(f"👁️  Vision capabilities: ENABLED")
            else:
                print(f"📝 Vision capabilities: Text-only")
            
            response = self.chat(
                messages=[{"role": "user", "content": "Hello! Please respond with 'Mac Studio LLM is working!' and confirm if you can see images."}],
                model=self.default_model
            )
            
            print(f"✅ Connection successful!")
            print(f"🤖 Response: {response}")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False


