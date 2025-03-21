from typing import List, Dict, Any
import numpy as np
from mesa import Model, Agent
from mesa.space import NetworkGrid
import networkx as nx
from datetime import datetime, timedelta
import random

from .agent import VillageResident, Demographics, Personality, Skills

class VillageModel(Model):
    def __init__(
        self,
        num_agents: int = 200,
        start_date: datetime = datetime(2025, 1, 1),
        simulation_years: int = 10,
        seed: int = None
    ):
        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.current_date = start_date
        self.end_date = start_date + timedelta(days=365 * simulation_years)
        
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
            'deaths': 0,
            'friendships': 0
        }
        
        # Создание начальной популяции
        self._create_initial_population()
        self._establish_initial_relationships()
        
    def _create_initial_population(self):
        """Создание начальной популяции агентов"""
        agents = []
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
            
            agents.append(agent)
            self.G.add_node(agent.unique_id)
        
        # Добавляем всех агентов в модель
        self.village_agents = agents
    
    def _establish_initial_relationships(self):
        """Установление начальных социальных связей"""
        # Создание семейных связей
        for agent in self.village_agents:
            # Вероятность создания связи зависит от социальности агента
            connection_probability = 0.1 + agent.personality.sociability * 0.2
            
            for other in self.village_agents:
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
    
    def update_relationship(self, agent1, agent2):
        """Обновление отношений между двумя жителями"""
        # Если они уже друзья, увеличиваем их счастье
        if agent2 in agent1.friends:
            agent1.happiness = min(1.0, agent1.happiness + 0.01)
            agent2.happiness = min(1.0, agent2.happiness + 0.01)
            return

        # Шанс подружиться зависит от их совместимости
        compatibility = self._calculate_compatibility(agent1, agent2)
        
        if random.random() < compatibility:
            # Становятся друзьями
            agent1.friends.append(agent2)
            agent2.friends.append(agent1)
            agent1.happiness = min(1.0, agent1.happiness + 0.05)
            agent2.happiness = min(1.0, agent2.happiness + 0.05)
            
            # Обновляем социальные метрики
            self.social_metrics['friendships'] += 1
            
            # Шанс на брак, если они подходят друг другу
            if (agent1.demographics.marital_status == 'single' and 
                agent2.demographics.marital_status == 'single' and
                agent1.demographics.gender != agent2.demographics.gender and
                abs(agent1.demographics.age - agent2.demographics.age) < 10):
                
                if random.random() < 0.1:  # 10% шанс на брак
                    agent1.demographics.marital_status = 'married'
                    agent2.demographics.marital_status = 'married'
                    agent1.family.append(agent2)
                    agent2.family.append(agent1)
                    self.social_metrics['marriages'] += 1

    def _calculate_compatibility(self, agent1, agent2):
        """Расчет совместимости между двумя жителями"""
        compatibility = 0.3  # Базовый шанс
        
        # Увеличиваем совместимость, если:
        # - Близкий возраст
        if abs(agent1.demographics.age - agent2.demographics.age) < 10:
            compatibility += 0.1
        
        # - Одинаковый уровень образования
        if agent1.demographics.education_level == agent2.demographics.education_level:
            compatibility += 0.1
        
        # - Работают в одной сфере
        if agent1.job == agent2.job:
            compatibility += 0.2
        
        # - Похожий уровень богатства
        if abs(agent1.wealth - agent2.wealth) < 1000:
            compatibility += 0.1
        
        return min(1.0, compatibility)

    def step(self):
        """Один шаг симуляции"""
        # Обновляем дату
        self.current_date += timedelta(days=1)
        
        # Обновляем состояние каждого жителя
        for agent in self.village_agents:
            # Обновление энергии
            agent.energy = min(1.0, agent.energy + random.uniform(0.1, 0.2))
            if agent.energy < 0.2:
                agent.happiness = max(0.0, agent.happiness - 0.1)
            
            # Обновление здоровья
            if random.random() < 0.05:  # 5% шанс изменения здоровья
                health_change = random.uniform(-0.1, 0.1)
                agent.health = max(0.0, min(1.0, agent.health + health_change))
            
            # Обновление богатства
            if agent.job:
                agent.wealth += random.randint(10, 50)  # Доход от работы
            
            # Расходы на жизнь
            agent.wealth = max(0, agent.wealth - random.randint(5, 20))
            
            # Влияние богатства на счастье
            if agent.wealth < 100:
                agent.happiness = max(0.0, agent.happiness - 0.1)
            elif agent.wealth > 1000:
                agent.happiness = min(1.0, agent.happiness + 0.05)
        
        # Обновляем экономику
        self._update_economy()
        
        # Обновляем социальные метрики
        self._update_social_metrics()
        
        # Еженедельный анализ
        if self.current_date.weekday() == 6:  # воскресенье
            self._weekly_analysis()
            
        # Ежемесячный анализ
        if self.current_date.day == 1:
            self._monthly_analysis()
    
    def _update_economy(self):
        """Обновление экономических показателей"""
        self.economy['total_wealth'] = sum(agent.wealth for agent in self.village_agents)
        # TODO: Реализовать более сложную экономическую логику
    
    def _update_social_metrics(self):
        """Обновление социальных показателей"""
        self.social_metrics['average_happiness'] = np.mean([agent.happiness for agent in self.village_agents])
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