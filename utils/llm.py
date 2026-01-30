"""
LLM Client
Unified interface for different LLM providers
"""

import os
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client supporting multiple providers"""
    
    def __init__(self):
        """Initialize LLM client"""
        self.provider = self._detect_provider()
        logger.info(f'Initialized LLM client with provider: {self.provider}')
    
    def _detect_provider(self) -> str:
        """Detect which LLM provider to use based on environment variables"""
        if os.getenv('OPENAI_API_KEY'):
            return 'openai'
        elif os.getenv('ANTHROPIC_API_KEY'):
            return 'anthropic'
        elif os.getenv('YANDEX_API_KEY'):
            return 'yandex'
        else:
            raise ValueError('No LLM provider configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or YANDEX_API_KEY')
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate text using configured LLM provider
        
        Args:
            system_prompt: System instruction
            user_prompt: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        try:
            if self.provider == 'openai':
                return self._generate_openai(system_prompt, user_prompt, temperature, max_tokens)
            elif self.provider == 'anthropic':
                return self._generate_anthropic(system_prompt, user_prompt, temperature, max_tokens)
            elif self.provider == 'yandex':
                return self._generate_yandex(system_prompt, user_prompt, temperature, max_tokens)
            else:
                raise ValueError(f'Unknown provider: {self.provider}')
        
        except Exception as e:
            logger.error(f'Error generating text: {str(e)}')
            raise
    
    def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate text using OpenAI API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f'OpenAI API error: {str(e)}')
            raise
    
    def _generate_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate text using Anthropic Claude API"""
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            model = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-5-20250929')
            
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {'role': 'user', 'content': user_prompt}
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f'Anthropic API error: {str(e)}')
            raise
    
    def _generate_yandex(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate text using Yandex GPT API"""
        try:
            api_key = os.getenv('YANDEX_API_KEY')
            folder_id = os.getenv('YANDEX_FOLDER_ID')
            model = os.getenv('YANDEX_MODEL', 'yandexgpt-lite')
            
            url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
            
            headers = {
                'Authorization': f'Api-Key {api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'modelUri': f'gpt://{folder_id}/{model}',
                'completionOptions': {
                    'temperature': temperature,
                    'maxTokens': str(max_tokens)
                },
                'messages': [
                    {
                        'role': 'system',
                        'text': system_prompt
                    },
                    {
                        'role': 'user',
                        'text': user_prompt
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['result']['alternatives'][0]['message']['text']
        
        except Exception as e:
            logger.error(f'Yandex GPT API error: {str(e)}')
            raise
    
    def test_connection(self) -> bool:
        """
        Test LLM connection
        
        Returns:
            True if connection is successful
        """
        try:
            response = self.generate(
                system_prompt='You are a helpful assistant.',
                user_prompt='Say "Hello" if you can hear me.',
                temperature=0.1,
                max_tokens=10
            )
            logger.info(f'LLM test successful: {response[:50]}')
            return True
        
        except Exception as e:
            logger.error(f'LLM test failed: {str(e)}')
            return False
