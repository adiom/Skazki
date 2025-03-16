from typing import List, Dict, Any
import numpy as np
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
import networkx as nx
from datetime import datetime, timedelta

from .agent import VillageResident, Demographics, Personality, Skills

class VillageModel(Model):
    def __init__(
        self,
        num_agents: int = 200,
        start_date: datetime = datetime(2025, 1, 1),
        simulation_years: int = 10
    ):
        super().__init__()
        self.num_agents = num_agents
        self.current_date = start_date
        self.end_date = start_date + timedelta(days=365 * simulation_years)
        
        # Инициализация планировщика
        self.schedule = RandomActivation(self)
        
        # Создание социальной сети
        self.G = nx.Graph()
        self.grid = NetworkGrid(self.G)
        
        # Экономические показатели деревни
        self.economy = {
            'total_wealth': 0.0,
            'resources': {
                'land': 1000,  # гектары
                'tools': 200,  # единицы
                'food': 5000,  # кг
                'materials': 1000  # единицы
            },
            'prices': {
                'food': 1.0,
                'tools': 5.0,
                'materials': 2.0
            }
        }
        
        # Социальные показатели
        self.social_metrics = {
            'average_happiness': 0.0,
            'conflicts': 0,
            'marriages': 0,
            'births': 0,
            'deaths': 0
        }
        
        # Создание начальной популяции
        self._create_initial_population()
        self._establish_initial_relationships()
        
    def _create_initial_population(self):
        """Создание начальной популяции агентов"""
        for i in range(self.num_agents):
            # Генерация демографических данных
            age = int(np.random.normal(30, 15))
            age = max(0, min(90, age))
            gender = np.random.choice(['M', 'F'])
            marital_status = np.random.choice(['single', 'married', 'widowed'], p=[0.3, 0.6, 0.1])
            education = np.random.choice(['none', 'basic', 'advanced'], p=[0.2, 0.7, 0.1])
            
            demographics = Demographics(
                age=age,
                gender=gender,
                marital_status=marital_status,
                education_level=education
            )
            
            # Генерация личностных характеристик
            personality = Personality(
                sociability=np.random.beta(2, 2),
                diligence=np.random.beta(2, 2),
                ambition=np.random.beta(2, 2),
                risk_tolerance=np.random.beta(2, 2)
            )
            
            # Генерация навыков
            skills = Skills(
                agriculture=np.random.beta(2, 2),
                crafts=np.random.beta(2, 2),
                trading=np.random.beta(2, 2),
                management=np.random.beta(2, 2)
            )
            
            agent = VillageResident(
                unique_id=i,
                model=self,
                demographics=demographics,
                personality=personality,
                skills=skills
            )
            
            self.schedule.add(agent)
            self.G.add_node(agent.unique_id)
    
    def _establish_initial_relationships(self):
        """Установление начальных социальных связей"""
        # Создание семейных связей
        agents = list(self.schedule.agents)
        for agent in agents:
            # Вероятность создания связи зависит от социальности агента
            connection_probability = 0.1 + agent.personality.sociability * 0.2
            
            for other in agents:
                if agent != other and np.random.random() < connection_probability:
                    self.G.add_edge(agent.unique_id, other.unique_id)
                    
                    # Определение типа связи
                    if abs(agent.demographics.age - other.demographics.age) <= 5:
                        agent.friends.append(other.unique_id)
                    elif abs(agent.demographics.age - other.demographics.age) >= 20:
                        if np.random.random() < 0.3:  # 30% шанс быть семьей
                            agent.family.append(other.unique_id)
                    
                    # Соседи (на основе случайной близости)
                    if np.random.random() < 0.2:
                        agent.neighbors.append(other.unique_id)
    
    def step(self):
        """Выполнение одного шага симуляции (один день)"""
        self.schedule.step()
        self.current_date += timedelta(days=1)
        
        # Обновление экономических показателей
        self._update_economy()
        
        # Обновление социальных метрик
        self._update_social_metrics()
        
        # Еженедельный анализ
        if self.current_date.weekday() == 6:  # воскресенье
            self._weekly_analysis()
            
        # Ежемесячный анализ
        if self.current_date.day == 1:
            self._monthly_analysis()
    
    def _update_economy(self):
        """Обновление экономических показателей"""
        self.economy['total_wealth'] = sum(agent.wealth for agent in self.schedule.agents)
        # TODO: Реализовать более сложную экономическую логику
    
    def _update_social_metrics(self):
        """Обновление социальных показателей"""
        agents = list(self.schedule.agents)
        self.social_metrics['average_happiness'] = np.mean([agent.happiness for agent in agents])
        # TODO: Обновление других социальных метрик
    
    def _weekly_analysis(self):
        """Еженедельный анализ"""
        # TODO: Реализовать анализ недельных показателей
        pass
    
    def _monthly_analysis(self):
        """Ежемесячный анализ"""
        # TODO: Реализовать анализ месячных показателей
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение текущей статистики модели"""
        return {
            'date': self.current_date,
            'population': self.num_agents,
            'economy': self.economy,
            'social_metrics': self.social_metrics
        } 