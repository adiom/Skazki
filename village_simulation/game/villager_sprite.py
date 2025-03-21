import pygame
import math
import random
from typing import Tuple, Optional, Dict
from village_simulation.src.agent import VillageResident

class VillagerSprite:
    def __init__(self, agent: VillageResident, initial_position: Tuple[int, int]):
        self.agent = agent
        self.position = list(initial_position)
        self.target: Optional[Tuple[int, int]] = None
        self.speed = 2
        self.size = 16
        self.color = self._get_color_by_job()
        
        # Анимация
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.direction = 'down'  # down, up, left, right
        self.is_moving = False
        
        # Задержка между движениями
        self.rest_timer = 0
        self.rest_duration = random.randint(1000, 3000)  # 1-3 секунды
    
    def _get_color_by_job(self) -> Tuple[int, int, int]:
        """Определение цвета жителя на основе его работы"""
        job_colors = {
            None: (200, 200, 200),  # Безработный
            'farmer': (0, 150, 0),  # Фермер
            'craftsman': (150, 75, 0),  # Ремесленник
            'trader': (0, 0, 150),  # Торговец
            'manager': (150, 0, 0)  # Управляющий
        }
        return job_colors.get(self.agent.job, (200, 200, 200))
    
    def move_to(self, target: Tuple[int, int]):
        """Установка новой цели движения"""
        self.target = target
        self.is_moving = True
        
        # Определение направления движения
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'
    
    def update(self):
        """Обновление позиции и состояния жителя"""
        if self.target and self.is_moving:
            # Вычисление вектора движения
            dx = self.target[0] - self.position[0]
            dy = self.target[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < self.speed:
                self.position[0] = self.target[0]
                self.position[1] = self.target[1]
                self.target = None
                self.is_moving = False
                self.rest_timer = pygame.time.get_ticks()
            else:
                # Нормализация вектора движения
                dx = dx / distance * self.speed
                dy = dy / distance * self.speed
                self.position[0] += dx
                self.position[1] += dy
                
                # Обновление направления
                if abs(dx) > abs(dy):
                    self.direction = 'right' if dx > 0 else 'left'
                else:
                    self.direction = 'down' if dy > 0 else 'up'
                
                # Обновление кадра анимации
                self.animation_frame += self.animation_speed
                if self.animation_frame >= 4:
                    self.animation_frame = 0
        elif not self.target and not self.is_moving:
            # Проверка времени отдыха
            current_time = pygame.time.get_ticks()
            if current_time - self.rest_timer >= self.rest_duration:
                self.is_moving = True
    
    def draw(self, screen):
        """Отрисовка жителя"""
        # Основная фигура
        rect = pygame.Rect(
            self.position[0] - self.size // 2,
            self.position[1] - self.size // 2,
            self.size,
            self.size
        )
        
        # Анимация движения
        if self.is_moving:
            offset = math.sin(self.animation_frame * math.pi) * 2
            rect.y += offset
        
        pygame.draw.rect(screen, self.color, rect)
        
        # Индикатор состояния
        status_color = self._get_status_color()
        pygame.draw.circle(
            screen,
            status_color,
            (int(self.position[0]), int(self.position[1] - self.size)),
            3
        )
    
    def _get_status_color(self) -> Tuple[int, int, int]:
        """Определение цвета индикатора состояния"""
        if self.agent.health < 0.3:
            return (255, 0, 0)  # Красный - плохое здоровье
        elif self.agent.happiness < 0.3:
            return (255, 165, 0)  # Оранжевый - несчастлив
        elif self.agent.energy < 0.3:
            return (128, 128, 128)  # Серый - устал
        return (0, 255, 0)  # Зеленый - все хорошо
    
    def get_info(self) -> Dict:
        """Получение информации о жителе"""
        return {
            "Возраст": f"{self.agent.demographics.age} лет",
            "Пол": "Мужской" if self.agent.demographics.gender == 'M' else "Женский",
            "Семейное положение": self.agent.demographics.marital_status,
            "Образование": self.agent.demographics.education_level,
            "Работа": self.agent.job or "Безработный",
            "Здоровье": f"{int(self.agent.health * 100)}%",
            "Счастье": f"{int(self.agent.happiness * 100)}%",
            "Энергия": f"{int(self.agent.energy * 100)}%",
            "Богатство": f"{int(self.agent.wealth)} монет",
            "Друзья": f"{len(self.agent.friends)} чел.",
            "Семья": f"{len(self.agent.family)} чел."
        } 