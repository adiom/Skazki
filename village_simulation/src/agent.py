from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
from mesa import Agent

@dataclass
class Demographics:
    age: int
    gender: str
    marital_status: str
    education_level: str

@dataclass
class Personality:
    sociability: float  # 0-1
    diligence: float   # 0-1
    ambition: float    # 0-1
    risk_tolerance: float  # 0-1

@dataclass
class Skills:
    agriculture: float  # 0-1
    crafts: float      # 0-1
    trading: float     # 0-1
    management: float  # 0-1

class VillageResident(Agent):
    def __init__(
        self,
        unique_id: int,
        model,
        demographics: Demographics,
        personality: Personality,
        skills: Skills
    ):
        super().__init__(model)
        self.unique_id = unique_id
        self.demographics = demographics
        self.personality = personality
        self.skills = skills
        
        # Социальные связи
        self.family: List[int] = []  # ID членов семьи
        self.friends: List[int] = []  # ID друзей
        self.colleagues: List[int] = []  # ID коллег
        self.neighbors: List[int] = []  # ID соседей
        
        # Экономические показатели
        self.wealth: float = 0.0
        self.income: float = 0.0
        self.job: Optional[str] = None
        self.owned_resources: Dict[str, float] = {}
        
        # Состояние
        self.health: float = 1.0  # 0-1
        self.happiness: float = 0.5  # 0-1
        self.energy: float = 1.0  # 0-1
        
    def step(self):
        """Ежедневные действия агента"""
        self._update_needs()
        self._plan_activities()
        self._perform_activities()
        self._update_state()
    
    def _update_needs(self):
        """Обновление потребностей агента"""
        # TODO: Реализовать логику обновления потребностей
        pass
    
    def _plan_activities(self):
        """Планирование действий на день"""
        # TODO: Реализовать логику планирования
        pass
    
    def _perform_activities(self):
        """Выполнение запланированных действий"""
        # TODO: Реализовать логику выполнения действий
        pass
    
    def _update_state(self):
        """Обновление состояния агента"""
        # Базовое обновление состояния
        self.energy = max(0.0, min(1.0, self.energy - 0.1 + np.random.normal(0.1, 0.05)))
        self.health = max(0.0, min(1.0, self.health + np.random.normal(0, 0.02)))
        self.happiness = max(0.0, min(1.0, self.happiness + np.random.normal(0, 0.05)))
        
    def interact_with(self, other_agent: 'VillageResident'):
        """Взаимодействие с другим агентом"""
        # TODO: Реализовать логику взаимодействия
        pass
    
    def age_up(self):
        """Увеличение возраста агента"""
        self.demographics.age += 1
        # TODO: Добавить логику изменения характеристик с возрастом
        
    def learn_skill(self, skill_name: str, amount: float):
        """Улучшение навыка"""
        if hasattr(self.skills, skill_name):
            current_value = getattr(self.skills, skill_name)
            setattr(self.skills, skill_name, min(1.0, current_value + amount))
            
    def get_social_status(self) -> float:
        """Расчет социального статуса"""
        # Простая формула для демонстрации
        return (
            len(self.family) * 0.2 +
            len(self.friends) * 0.1 +
            self.wealth * 0.3 +
            max(self.skills.__dict__.values()) * 0.4
        ) 