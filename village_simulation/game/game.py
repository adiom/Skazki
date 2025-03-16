import pygame
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import random
from village_simulation.src.village_model import VillageModel
from village_simulation.game.villager_sprite import VillagerSprite

# Константы
TILE_SIZE = 32
GRID_WIDTH = 50
GRID_HEIGHT = 40
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Цвета
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GRAY': (128, 128, 128),
    'GREEN': (34, 139, 34),
    'BLUE': (30, 144, 255),
    'YELLOW': (255, 255, 0),
    'ORANGE': (255, 165, 0),
    'BROWN': (139, 69, 19)
}

@dataclass
class GameObject:
    type: str
    position: Tuple[int, int]
    size: Tuple[int, int]
    color: Tuple[int, int, int]
    name: str
    info: Dict

class VillageGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Симуляция деревни")
        
        # Инициализация модели
        self.model = VillageModel()
        
        # Игровые объекты
        self.objects: List[GameObject] = []
        self.selected_object: Optional[GameObject] = None
        
        # Жители
        self.villagers: List[VillagerSprite] = []
        self.selected_villager: Optional[VillagerSprite] = None
        
        # Создание базовых объектов и жителей
        self._create_initial_objects()
        self._create_villagers()
        
        # Шрифты
        self.font = pygame.font.Font(None, 24)
        
        # Флаги
        self.running = True
        self.show_info = False
        
        # Таймер для обновления целей жителей
        self.last_target_update = 0
        self.target_update_interval = 5000  # 5 секунд
    
    def _create_initial_objects(self):
        """Создание начальных объектов на карте"""
        # Примеры инфраструктуры
        self.objects.extend([
            # Водонапорная башня
            GameObject(
                type="water_tower",
                position=(5, 5),
                size=(2, 2),
                color=COLORS['BLUE'],
                name="Водонапорная башня",
                info={"состояние": "работает", "обслуживает": "50 жителей"}
            ),
            # Солнечная электростанция
            GameObject(
                type="solar_plant",
                position=(10, 5),
                size=(3, 2),
                color=COLORS['YELLOW'],
                name="Солнечная электростанция",
                info={"состояние": "работает", "мощность": "100 кВт"}
            ),
            # Газовая станция
            GameObject(
                type="gas_station",
                position=(15, 5),
                size=(2, 2),
                color=COLORS['ORANGE'],
                name="Газовая станция",
                info={"состояние": "работает", "запас": "80%"}
            ),
            # Банк
            GameObject(
                type="bank",
                position=(20, 5),
                size=(2, 2),
                color=COLORS['GRAY'],
                name="Банк",
                info={"состояние": "работает", "клиенты": "120 жителей"}
            )
        ])
        
    def _create_villagers(self):
        """Создание жителей на карте"""
        for agent in self.model.schedule.agents:
            # Случайная позиция на карте
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            
            villager = VillagerSprite(agent, (x, y))
            self.villagers.append(villager)
    
    def _update_villagers(self):
        """Обновление состояния жителей"""
        current_time = pygame.time.get_ticks()
        
        # Обновление целей движения
        if current_time - self.last_target_update > self.target_update_interval:
            for villager in self.villagers:
                if not villager.target:  # Если нет текущей цели
                    # Выбор случайной точки на карте
                    new_x = random.randint(0, WINDOW_WIDTH)
                    new_y = random.randint(0, WINDOW_HEIGHT)
                    villager.move_to((new_x, new_y))
            
            self.last_target_update = current_time
        
        # Обновление позиций
        for villager in self.villagers:
            villager.update()
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    self._handle_click(event.pos)
    
    def _handle_click(self, pos: Tuple[int, int]):
        """Обработка клика мышью"""
        # Сброс выделения
        self.selected_object = None
        self.selected_villager = None
        self.show_info = False
        
        # Проверка клика по жителям
        for villager in self.villagers:
            dx = pos[0] - villager.position[0]
            dy = pos[1] - villager.position[1]
            if (dx * dx + dy * dy) <= (villager.size * villager.size):
                self.selected_villager = villager
                self.show_info = True
                return
        
        # Проверка клика по объектам
        grid_x = pos[0] // TILE_SIZE
        grid_y = pos[1] // TILE_SIZE
        
        for obj in self.objects:
            obj_rect = pygame.Rect(
                obj.position[0] * TILE_SIZE,
                obj.position[1] * TILE_SIZE,
                obj.size[0] * TILE_SIZE,
                obj.size[1] * TILE_SIZE
            )
            if obj_rect.collidepoint(pos):
                self.selected_object = obj
                self.show_info = True
                break
    
    def draw(self):
        """Отрисовка игры"""
        self.screen.fill(COLORS['GREEN'])  # Фон - трава
        
        # Отрисовка сетки
        for x in range(0, WINDOW_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, COLORS['BLACK'], (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, COLORS['BLACK'], (0, y), (WINDOW_WIDTH, y), 1)
        
        # Отрисовка объектов
        for obj in self.objects:
            rect = pygame.Rect(
                obj.position[0] * TILE_SIZE,
                obj.position[1] * TILE_SIZE,
                obj.size[0] * TILE_SIZE,
                obj.size[1] * TILE_SIZE
            )
            pygame.draw.rect(self.screen, obj.color, rect)
            
            # Название объекта
            text = self.font.render(obj.name, True, COLORS['BLACK'])
            text_rect = text.get_rect(center=(
                rect.centerx,
                rect.top - 10
            ))
            self.screen.blit(text, text_rect)
        
        # Отрисовка жителей
        for villager in self.villagers:
            villager.draw(self.screen)
        
        # Отрисовка информационного окна
        if self.show_info:
            if self.selected_villager:
                self._draw_villager_info()
            elif self.selected_object:
                self._draw_object_info()
        
        pygame.display.flip()
    
    def _draw_villager_info(self):
        """Отрисовка информации о жителе"""
        if not self.selected_villager:
            return
            
        # Параметры окна
        window_width = 300
        window_height = 250
        window_x = WINDOW_WIDTH - window_width - 10
        window_y = 10
        
        # Фон окна
        info_surface = pygame.Surface((window_width, window_height))
        info_surface.fill(COLORS['WHITE'])
        pygame.draw.rect(info_surface, COLORS['BLACK'], 
                        info_surface.get_rect(), 2)
        
        # Информация
        info = self.selected_villager.get_info()
        y = 10
        for key, value in info.items():
            text = self.font.render(f"{key}: {value}", True, COLORS['BLACK'])
            info_surface.blit(text, (10, y))
            y += 30
        
        self.screen.blit(info_surface, (window_x, window_y))
    
    def _draw_object_info(self):
        """Отрисовка информации об объекте"""
        if not self.selected_object:
            return
            
        # Параметры окна
        window_width = 300
        window_height = 200
        window_x = WINDOW_WIDTH - window_width - 10
        window_y = 10
        
        # Фон окна
        info_surface = pygame.Surface((window_width, window_height))
        info_surface.fill(COLORS['WHITE'])
        pygame.draw.rect(info_surface, COLORS['BLACK'], 
                        info_surface.get_rect(), 2)
        
        # Заголовок
        title = self.font.render(self.selected_object.name, True, COLORS['BLACK'])
        info_surface.blit(title, (10, 10))
        
        # Информация
        y = 50
        for key, value in self.selected_object.info.items():
            text = self.font.render(f"{key}: {value}", True, COLORS['BLACK'])
            info_surface.blit(text, (10, y))
            y += 30
        
        self.screen.blit(info_surface, (window_x, window_y))
    
    def run(self):
        """Главный игровой цикл"""
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            self._update_villagers()
            self.draw()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = VillageGame()
    game.run() 