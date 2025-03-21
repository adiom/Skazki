import requests
import json
import logging
import time
import os
from typing import Dict, List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pygame

class AIController:
    def __init__(self):
        self.logger = logging.getLogger('ai_debug')
        
        # Конфигурация API
        self.api_type = os.getenv('AI_API_TYPE', 'openrouter')  # openrouter, lmstudio, или vercel
        
        if self.api_type == 'openrouter':
            # Получаем API ключ из переменной окружения или используем резервный ключ
            self.api_key = os.getenv('OPENROUTER_API_KEY', 
                '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')
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            self.model = "google/gemini-2.0-pro-exp-02-05:free"  # или другая быстрая модель
        elif self.api_type == 'lmstudio':
            self.api_url = "http://localhost:1234/v1/chat/completions"
            self.model = "local-model"
        elif self.api_type == 'vercel':
            self.api_key = os.getenv('VERCEL_AI_API_KEY')
            self.api_url = "https://api.vercel.ai/v1/chat/completions"
            self.model = "gemini-pro"
        
        # Настройка сессии с повторными попытками
        self.session = requests.Session()
        retries = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        
        # Системный промпт для ИИ
        self.system_prompt = """Ты - ИИ-советник по управлению деревней. Твоя задача - анализировать состояние деревни и предлагать конкретные действия для улучшения ситуации.

Ответ должен быть в формате JSON:
{
    "analysis": "Краткий анализ ситуации",
    "actions": [
        {
            "type": "DISTRIBUTE_RESOURCES | CREATE_JOBS | INVEST | ADJUST_PRICES | ORGANIZE_EVENT",
            "target": "Конкретная цель действия",
            "value": число или строка,
            "priority": число от 1 до 5
        }
    ]
}"""

    def send_request(self, prompt: str) -> Optional[Dict]:
        """Отправка запроса к API"""
        try:
            self.logger.debug(f"Отправка запроса к {self.api_type}")
            
            headers = {"Content-Type": "application/json"}
            if self.api_type == 'openrouter':
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["HTTP-Referer"] = "https://github.com/your-repo"  # требуется для OpenRouter
                headers["X-Title"] = "Village Simulation Game"
            elif self.api_type == 'vercel':
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            payload = {
                "messages": messages,
                "model": self.model,
                "temperature": 0.7,
                "max_tokens": 800,
                "stream": False
            }
            
            # Отправляем запрос
            response = self.session.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30  # уменьшаем таймаут для быстрых моделей
            )
            
            self.logger.debug(f"Получен ответ: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"Тело ответа: {data}")
                    
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        self.logger.debug(f"Содержимое ответа: {content}")
                        
                        # Извлекаем JSON из ответа
                        import re
                        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            return json.loads(json_str)
                        else:
                            # Пробуем распарсить весь ответ как JSON
                            try:
                                return json.loads(content)
                            except:
                                self.logger.warning("Не удалось распарсить JSON")
                                return None
                except Exception as e:
                    self.logger.error(f"Ошибка обработки ответа: {str(e)}")
                    return None
            else:
                self.logger.error(f"Ошибка API: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка запроса: {str(e)}")
            return None
    
    def interpret_response(self, response: Dict) -> List[Dict]:
        """Интерпретация ответа от ИИ"""
        try:
            self.logger.debug(f"Начало интерпретации ответа: {response}")
            
            if not isinstance(response, dict):
                self.logger.error(f"Неверный формат ответа: {type(response)}")
                return []
            
            if 'actions' not in response:
                self.logger.error("В ответе отсутствует поле 'actions'")
                return []
            
            actions = []
            for action in response['actions']:
                if self._validate_action(action):
                    actions.append(action)
            
            self.logger.debug(f"Интерпретировано {len(actions)} действий")
            return sorted(actions, key=lambda x: x.get('priority', 5))
            
        except Exception as e:
            self.logger.error(f"Ошибка при интерпретации ответа: {str(e)}", exc_info=True)
            return []
    
    def _validate_action(self, action: Dict) -> bool:
        """Проверка корректности действия"""
        try:
            required_fields = ['type', 'target', 'value', 'priority']
            if not all(field in action for field in required_fields):
                self.logger.warning(f"Действию не хватает обязательных полей: {action}")
                return False
            
            valid_types = {
                'DISTRIBUTE_RESOURCES',
                'CREATE_JOBS',
                'INVEST',
                'ADJUST_PRICES',
                'ORGANIZE_EVENT'
            }
            
            if action['type'] not in valid_types:
                self.logger.warning(f"Неверный тип действия: {action['type']}")
                return False
            
            # Проверка приоритета
            try:
                priority = int(action['priority'])
                if not (1 <= priority <= 5):
                    self.logger.warning(f"Неверный приоритет: {priority}")
                    return False
            except (ValueError, TypeError):
                self.logger.warning(f"Неверный формат приоритета: {action['priority']}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при валидации действия: {str(e)}")
            return False

    def _update_model(self):
        if self.paused:
            return
        
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_model_update > self.model_update_interval / self.game_speed:
            # ... существующий код ...
            
            # Обновление строительства
            self._update_constructions() 