import pygame
from typing import Tuple, Dict
import random
from village_simulation.src.agent import VillageResident

class VillagerSprite:
    def __init__(self, resident: VillageResident, position: Tuple[int, int]):
        self.resident = resident
        self.position = list(position)  # [x, y] в пикселях
        self.target = None  # цель движения
        self.speed = 2  # пикселей за кадр
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
        self.size = 16  # размер спрайта
        
    def move_to(self, target: Tuple[int, int]):
        """Установка новой цели движения"""
        self.target = list(target)
    
    def update(self):
        """Обновление позиции жителя"""
        if self.target:
            dx = self.target[0] - self.position[0]
            dy = self.target[1] - self.position[1]
            
            # Если достигли цели с погрешностью в 2 пикселя
            if abs(dx) < 2 and abs(dy) < 2:
                self.position = self.target
                self.target = None
                return
            
            # Нормализация вектора движения
            distance = (dx * dx + dy * dy) ** 0.5
            if distance > 0:
                dx = dx / distance * self.speed
                dy = dy / distance * self.speed
                
                self.position[0] += dx
                self.position[1] += dy
    
    def draw(self, screen: pygame.Surface):
        """Отрисовка жителя"""
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position[0]), int(self.position[1])),
            self.size // 2
        )
    
    def get_info(self) -> Dict:
        """Получение информации о жителе"""
        return {
            "Имя": f"Житель #{self.resident.unique_id}",
            "Возраст": f"{self.resident.demographics.age} лет",
            "Пол": "Мужской" if self.resident.demographics.gender == 'M' else "Женский",
            "Семейное положение": self.resident.demographics.marital_status,
            "Образование": self.resident.demographics.education_level,
            "Здоровье": f"{int(self.resident.health * 100)}%",
            "Счастье": f"{int(self.resident.happiness * 100)}%"
        } 