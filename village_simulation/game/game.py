import pygame
import sys
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import random
import os
from village_simulation.src.village_model import VillageModel
from village_simulation.game.villager_sprite import VillagerSprite
from village_simulation.ai.ai_controller import AIController
from dotenv import load_dotenv

# Обновленные константы для интерфейса
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILE_SIZE = 32
GRID_WIDTH = 100
GRID_HEIGHT = 80
CAMERA_EDGE_SIZE = 20  # Размер области у края экрана для движения камеры
CAMERA_SPEED = 10  # Скорость движения камеры

# Новые константы интерфейса
UI = {
    'PANEL_HEIGHT': 200,  # Высота нижней панели
    'TOP_BAR_HEIGHT': 60, # Высота верхней панели
    'SIDE_PANEL': 250,    # Ширина боковой панели
    'MINIMAP_SIZE': 200   # Размер мини-карты
}

STATS_PANEL_WIDTH = UI['SIDE_PANEL']  # Ширина панели статистики

# Обновленные цвета
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GRAY': (128, 128, 128),
    'DARK_BLUE': (0, 20, 40, 230),    # Фон панелей
    'LIGHT_BLUE': (0, 128, 255),      # Рамки
    'BUTTON_NORMAL': (0, 40, 80),     # Обычная кнопка
    'BUTTON_HOVER': (0, 60, 120),     # Кнопка при наведении
    'BUTTON_ACTIVE': (0, 80, 160),    # Активная кнопка
    'TEXT': (180, 220, 255),         # Цвет текста
    'GREEN': (34, 139, 34),
    'BLUE': (30, 144, 255),
    'YELLOW': (255, 255, 0),
    'ORANGE': (255, 165, 0),
    'RED': (255, 0, 0)
}

# Типы тайлов
TILES = {
    'GRASS': 0,
    'PATH': 1,
    'WATER': 2,
    'FARM': 3,
    'HOUSE': 4
}

@dataclass
class GameObject:
    type: str
    position: Tuple[int, int]
    size: Tuple[int, int]
    color: Tuple[int, int, int]
    name: str
    info: Dict

class ModernButton:
    def __init__(self, x, y, width, height, text, icon="", tooltip=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.tooltip = tooltip
        self.hover = False
        self.active = False
        
    def draw(self, screen, font):
        # Определяем цвет кнопки
        color = COLORS['BUTTON_ACTIVE'] if self.active else \
                COLORS['BUTTON_HOVER'] if self.hover else \
                COLORS['BUTTON_NORMAL']
        
        # Рисуем кнопку с закругленными углами
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLORS['LIGHT_BLUE'], self.rect, 2, border_radius=5)
        
        # Отрисовка иконки и текста
        content = f"{self.icon} {self.text}" if self.icon else self.text
        text_surface = font.render(content, True, COLORS['TEXT'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
        # Подсказка при наведении
        if self.hover and self.tooltip:
            tooltip_surface = font.render(self.tooltip, True, COLORS['TEXT'])
            tooltip_rect = tooltip_surface.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 5))
            pygame.draw.rect(screen, COLORS['DARK_BLUE'], tooltip_rect.inflate(20, 10), border_radius=3)
            screen.blit(tooltip_surface, tooltip_rect)

class VillageGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Симуляция деревни")
        
        # Настройка логирования
        self.setup_logging()
        self.logger.info("Игра запущена")
        
        # Камера
        self.camera_x = 0
        self.camera_y = 0
        self.world_surface = pygame.Surface((GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE))
        
        # Инициализация модели
        self.model = VillageModel()
        
        # Временные параметры
        self.game_speed = 1  # Скорость течения времени (1 = нормальная)
        self.last_model_update = 0
        self.model_update_interval = 1000  # Обновление модели каждую секунду
        self.paused = False  # Флаг паузы
        
        # Обновленные кнопки
        button_y = WINDOW_HEIGHT - UI['PANEL_HEIGHT'] + 10
        self.buttons = {
            # Управление
            'pause': ModernButton(10, 10, 120, 40, "Пауза", "⏸️", "Пауза/Продолжить"),
            'speed_up': ModernButton(140, 10, 120, 40, "Быстрее", "⏩", "Ускорить время"),
            'speed_down': ModernButton(270, 10, 120, 40, "Медленнее", "⏪", "Замедлить время"),
            
            # Строительство
            'build_house': ModernButton(10, button_y, 150, 40, "Жилой дом", "🏠", "1000 ресурсов"),
            'build_farm': ModernButton(170, button_y, 150, 40, "Ферма", "🏡", "2000 ресурсов"),
            'build_factory': ModernButton(330, button_y, 150, 40, "Фабрика", "🏭", "5000 ресурсов"),
            
            # Графики
            'show_stats': ModernButton(10, button_y + 50, 150, 40, "Статистика", "📊", "Показать графики"),
            'show_jobs': ModernButton(170, button_y + 50, 150, 40, "Работа", "👥", "Занятость"),
            'show_resources': ModernButton(330, button_y + 50, 150, 40, "Ресурсы", "📦", "Ресурсы")
        }
        
        # Графики
        self.show_graphs = False
        self.stats_history = {
            'happiness': [],
            'wealth': [],
            'population': [],
            'resources': {
                'food': [],
                'tools': [],
                'materials': []
            }
        }
        
        # Карта тайлов
        self.tile_map = [[TILES['GRASS'] for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.communication_lines = []  # Линии коммуникаций между объектами
        
        # Игровые объекты
        self.objects: List[GameObject] = []
        self.selected_object: Optional[GameObject] = None
        
        # Жители
        self.villagers: List[VillagerSprite] = []
        self.selected_villager: Optional[VillagerSprite] = None
        
        # Создание базовых объектов и жителей
        self._create_initial_map()
        self._create_initial_objects()
        self._create_villagers()
        self._create_communication_lines()
        
        # Шрифты
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Флаги
        self.running = True
        self.show_info = False
        
        # Таймер для обновления
        self.last_target_update = 0
        self.target_update_interval = 5000
        
        # Статистика
        self.stats_update_timer = 0
        self.stats_update_interval = 1000
        
        # ИИ всегда активен
        self.ai_control = True
        self.last_ai_update = 0  # Начинаем с 0, чтобы первый запрос произошел сразу
        self.ai_update_interval = 90000  # 90 секунд между запросами
        self.ai_request_in_progress = False
        self.ai_last_request_time = 0
        self.ai_request_timeout = 30000  # 30 секунд таймаут
        self.ai_action_queue = []
        
        # Инициализация AI контроллера
        self.ai_controller = AIController()
        
        # Загружаем конфигурацию из .env файла
        load_dotenv()
        
        self.logger.info("ИИ инициализирован и активен")
    
    def setup_logging(self):
        """Настройка системы логирования"""
        # Основной логгер
        self.logger = logging.getLogger('village_simulation')
        self.logger.setLevel(logging.INFO)
        
        # Создание файла лога с текущей датой
        log_filename = f"logs/village_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ai_log_filename = f"logs/ai_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        os.makedirs('logs', exist_ok=True)
        
        # Настройка основного логгера
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Отдельный логгер для ИИ
        self.ai_logger = logging.getLogger('ai_debug')
        self.ai_logger.setLevel(logging.DEBUG)
        
        ai_handler = logging.FileHandler(ai_log_filename)
        ai_handler.setLevel(logging.DEBUG)
        ai_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ai_handler.setFormatter(ai_formatter)
        self.ai_logger.addHandler(ai_handler)
        
        # Добавляем вывод в консоль для отладки ИИ
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ai_formatter)
        self.ai_logger.addHandler(console_handler)
    
    def _create_initial_map(self):
        """Создание начальной карты с дорожками и различными типами местности"""
        # Создание основных дорог
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                # Главные дороги
                if x % 10 == 0 or y % 10 == 0:
                    self.tile_map[y][x] = TILES['PATH']
                # Случайные участки воды
                elif random.random() < 0.02:
                    self.tile_map[y][x] = TILES['WATER']
                # Случайные фермы
                elif random.random() < 0.05:
                    self.tile_map[y][x] = TILES['FARM']

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
        for agent in self.model.village_agents:
            # Случайная позиция на карте
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            
            villager = VillagerSprite(agent, (x, y))
            self.villagers.append(villager)
    
    def _create_communication_lines(self):
        """Создание линий коммуникаций между объектами"""
        for obj1 in self.objects:
            for obj2 in self.objects:
                if obj1 != obj2:
                    if random.random() < 0.3:  # 30% шанс создания связи
                        start = (
                            obj1.position[0] * TILE_SIZE + obj1.size[0] * TILE_SIZE // 2,
                            obj1.position[1] * TILE_SIZE + obj1.size[1] * TILE_SIZE // 2
                        )
                        end = (
                            obj2.position[0] * TILE_SIZE + obj2.size[0] * TILE_SIZE // 2,
                            obj2.position[1] * TILE_SIZE + obj2.size[1] * TILE_SIZE // 2
                        )
                        self.communication_lines.append((start, end))
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Обработка нажатий на кнопки
                for name, button in self.buttons.items():
                    if button.rect.collidepoint(mouse_pos):
                        self._handle_button_click(name)
                        break
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons.values():
                    button.hover = button.rect.collidepoint(mouse_pos)
    
    def _handle_camera_movement(self):
        """Обработка движения камеры"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Движение камеры от положения мыши у края экрана
        if mouse_pos[0] < CAMERA_EDGE_SIZE:
            self.camera_x = max(0, self.camera_x - CAMERA_SPEED)
        elif mouse_pos[0] > WINDOW_WIDTH - CAMERA_EDGE_SIZE - STATS_PANEL_WIDTH:
            self.camera_x = min(GRID_WIDTH * TILE_SIZE - (WINDOW_WIDTH - STATS_PANEL_WIDTH), 
                              self.camera_x + CAMERA_SPEED)
        
        if mouse_pos[1] < CAMERA_EDGE_SIZE:
            self.camera_y = max(0, self.camera_y - CAMERA_SPEED)
        elif mouse_pos[1] > WINDOW_HEIGHT - CAMERA_EDGE_SIZE:
            self.camera_y = min(GRID_HEIGHT * TILE_SIZE - WINDOW_HEIGHT, 
                              self.camera_y + CAMERA_SPEED)
        
        # Движение камеры с помощью клавиш WASD
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.camera_x = max(0, self.camera_x - CAMERA_SPEED)
        if keys[pygame.K_d]:
            self.camera_x = min(GRID_WIDTH * TILE_SIZE - (WINDOW_WIDTH - STATS_PANEL_WIDTH), 
                              self.camera_x + CAMERA_SPEED)
        if keys[pygame.K_w]:
            self.camera_y = max(0, self.camera_y - CAMERA_SPEED)
        if keys[pygame.K_s]:
            self.camera_y = min(GRID_HEIGHT * TILE_SIZE - WINDOW_HEIGHT, 
                              self.camera_y + CAMERA_SPEED)
    
    def _handle_click(self, pos: Tuple[int, int]):
        """Обработка клика мышью"""
        # Преобразование координат экрана в координаты мира
        world_x = pos[0] + self.camera_x
        world_y = pos[1] + self.camera_y
        
        # Сброс выделения
        self.selected_object = None
        self.selected_villager = None
        self.show_info = False
        
        # Проверка клика по жителям
        for villager in self.villagers:
            dx = world_x - villager.position[0]
            dy = world_y - villager.position[1]
            if (dx * dx + dy * dy) <= (villager.size * villager.size):
                self.selected_villager = villager
                self.show_info = True
                return
        
        # Проверка клика по объектам
        grid_x = world_x // TILE_SIZE
        grid_y = world_y // TILE_SIZE
        
        for obj in self.objects:
            obj_rect = pygame.Rect(
                obj.position[0] * TILE_SIZE,
                obj.position[1] * TILE_SIZE,
                obj.size[0] * TILE_SIZE,
                obj.size[1] * TILE_SIZE
            )
            if obj_rect.collidepoint(world_x, world_y):
                self.selected_object = obj
                self.show_info = True
                break
    
    def draw(self):
        """Отрисовка игры"""
        # Очистка экрана
        self.screen.fill(COLORS['BLACK'])
        
        # Отрисовка мира
        self._draw_game_world()
        
        # Интерфейс
        self._draw_top_panel()
        self._draw_bottom_panel()
        self._draw_side_panel()
        self._draw_minimap()
        
        # Графики
        if self.show_graphs:
            self._draw_graphs()
        
        pygame.display.flip()
    
    def _draw_game_world(self):
        """Отрисовка игрового мира"""
        # Очищаем поверхность мира
        self.world_surface.fill(COLORS['DARK_BLUE'])
        
        # Отрисовка тайлов карты
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile_type = self.tile_map[y][x]
                color = COLORS['GREEN'] if tile_type == TILES['GRASS'] else \
                       COLORS['BLUE'] if tile_type == TILES['WATER'] else \
                       COLORS['YELLOW'] if tile_type == TILES['PATH'] else \
                       COLORS['ORANGE'] if tile_type == TILES['FARM'] else \
                       COLORS['RED'] if tile_type == TILES['HOUSE'] else \
                       COLORS['GRAY']
                
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.world_surface, color, rect)
                pygame.draw.rect(self.world_surface, COLORS['BLACK'], rect, 1)
        
        # Отрисовка объектов
        for obj in self.objects:
            x, y = obj.position
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, 
                              obj.size[0] * TILE_SIZE, obj.size[1] * TILE_SIZE)
            pygame.draw.rect(self.world_surface, obj.color, rect)
            pygame.draw.rect(self.world_surface, COLORS['BLACK'], rect, 2)
        
        # Отрисовка жителей
        for villager in self.villagers:
            x, y = villager.position
            rect = pygame.Rect(int(x), int(y), 
                              int(TILE_SIZE / 2), int(TILE_SIZE / 2))
            pygame.draw.rect(self.world_surface, COLORS['RED'], rect)
        
        # Отображение world_surface на экран с учетом камеры
        visible_rect = pygame.Rect(self.camera_x, self.camera_y, 
                                  WINDOW_WIDTH - STATS_PANEL_WIDTH, WINDOW_HEIGHT)
        self.screen.blit(self.world_surface, (0, 0), visible_rect)
    
    def _draw_top_panel(self):
        panel = pygame.Surface((WINDOW_WIDTH, UI['TOP_BAR_HEIGHT']), pygame.SRCALPHA)
        panel.fill(COLORS['DARK_BLUE'])
        
        # Кнопки управления
        self.buttons['pause'].draw(panel, self.font)
        self.buttons['speed_up'].draw(panel, self.font)
        self.buttons['speed_down'].draw(panel, self.font)
        
        # Ресурсы
        x = 400
        resources = [
            ("💰", self.model.economy['total_wealth']),
            ("🌾", self.model.economy['resources']['food']),
            ("⚒️", self.model.economy['resources']['tools']),
            ("📦", self.model.economy['resources']['materials'])
        ]
        
        for icon, value in resources:
            text = f"{icon} {int(value)}"
            color = COLORS['GREEN'] if value > 0 else COLORS['RED']
            text_surface = self.font.render(text, True, color)
            panel.blit(text_surface, (x, 15))
            x += 150
        
        self.screen.blit(panel, (0, 0))

    def _draw_bottom_panel(self):
        panel = pygame.Surface((WINDOW_WIDTH - STATS_PANEL_WIDTH, UI['PANEL_HEIGHT']), pygame.SRCALPHA)
        panel.fill(COLORS['DARK_BLUE'])
        
        # Кнопки меню
        self.buttons['build_house'].draw(panel, self.font)
        self.buttons['build_farm'].draw(panel, self.font)
        self.buttons['build_factory'].draw(panel, self.font)
        self.buttons['show_stats'].draw(panel, self.font)
        self.buttons['show_jobs'].draw(panel, self.font)
        self.buttons['show_resources'].draw(panel, self.font)
        
        self.screen.blit(panel, (0, WINDOW_HEIGHT - UI['PANEL_HEIGHT']))
    
    def _draw_side_panel(self):
        """Отрисовка боковой панели с информацией"""
        panel = pygame.Surface((STATS_PANEL_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        panel.fill(COLORS['DARK_BLUE'])
        
        # Заголовок
        title = self.font.render("Информация", True, COLORS['TEXT'])
        panel.blit(title, (STATS_PANEL_WIDTH // 2 - title.get_width() // 2, 10))
        
        # Статистика поселения
        stats_y = 70
        stats = [
            f"Население: {len(self.model.village_agents)}",
            f"Счастье: {self.model.social_metrics['average_happiness']:.1f}",
            f"Богатство: {self.model.economy['total_wealth']}",
            f"Еда: {self.model.economy['resources'].get('food', 0)}",
            f"Инструменты: {self.model.economy['resources'].get('tools', 0)}",
            f"Дома: {sum(1 for obj in self.objects if obj.type == 'house')}",
            f"Фермы: {sum(1 for obj in self.objects if obj.type == 'farm')}",
            f"Фабрики: {sum(1 for obj in self.objects if obj.type == 'factory')}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, COLORS['TEXT'])
            panel.blit(text, (20, stats_y + i * 30))
        
        self.screen.blit(panel, (WINDOW_WIDTH - STATS_PANEL_WIDTH, 0))
    
    def _draw_minimap(self):
        """Отрисовка мини-карты"""
        minimap_size = UI['MINIMAP_SIZE']
        minimap = pygame.Surface((minimap_size, minimap_size))
        minimap.fill(COLORS['DARK_BLUE'])
        
        # Масштаб мини-карты
        scale_x = minimap_size / (GRID_WIDTH * TILE_SIZE)
        scale_y = minimap_size / (GRID_HEIGHT * TILE_SIZE)
        
        # Отрисовка карты в миниатюре
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile_type = self.tile_map[y][x]
                color = COLORS['GREEN'] if tile_type == TILES['GRASS'] else \
                       COLORS['BLUE'] if tile_type == TILES['WATER'] else \
                       COLORS['YELLOW'] if tile_type == TILES['PATH'] else \
                       COLORS['ORANGE'] if tile_type == TILES['FARM'] else \
                       COLORS['RED'] if tile_type == TILES['HOUSE'] else \
                       COLORS['GRAY']
                
                mini_x = int(x * TILE_SIZE * scale_x)
                mini_y = int(y * TILE_SIZE * scale_y)
                mini_w = max(1, int(TILE_SIZE * scale_x))
                mini_h = max(1, int(TILE_SIZE * scale_y))
                
                pygame.draw.rect(minimap, color, (mini_x, mini_y, mini_w, mini_h))
        
        # Отображение текущего видимого прямоугольника камеры
        view_rect = pygame.Rect(
            int(self.camera_x * scale_x),
            int(self.camera_y * scale_y),
            int((WINDOW_WIDTH - STATS_PANEL_WIDTH) * scale_x),
            int(WINDOW_HEIGHT * scale_y)
        )
        pygame.draw.rect(minimap, COLORS['WHITE'], view_rect, 2)
        
        # Размещение мини-карты на экране
        self.screen.blit(minimap, (WINDOW_WIDTH - STATS_PANEL_WIDTH + 20, 
                                 WINDOW_HEIGHT - minimap_size - 20))
    
    def _draw_graphs(self):
        graph_surface = pygame.Surface((600, 400))
        graph_surface.fill(COLORS['DARK_BLUE'])
        
        # Рисуем графики
        if self.stats_history['happiness']:
            points = [(i * 2, 380 - val * 360) for i, val in enumerate(self.stats_history['happiness'][-300:])]
            if len(points) > 1:
                pygame.draw.lines(graph_surface, COLORS['GREEN'], False, points, 2)
        
        if self.stats_history['wealth']:
            max_wealth = max(self.stats_history['wealth'])
            if max_wealth > 0:
                points = [(i * 2, 380 - (val / max_wealth) * 360) 
                         for i, val in enumerate(self.stats_history['wealth'][-300:])]
                if len(points) > 1:
                    pygame.draw.lines(graph_surface, COLORS['YELLOW'], False, points, 2)
        
        # Отображаем графики по центру экрана
        self.screen.blit(graph_surface, 
                        ((WINDOW_WIDTH - 600) // 2, 
                         (WINDOW_HEIGHT - 400) // 2))

    def _handle_button_click(self, button_name):
        if button_name == 'pause':
            self.paused = not self.paused
            self.buttons['pause'].text = "▶️ Старт" if self.paused else "⏸️ Пауза"
        
        elif button_name == 'speed_up':
            self.game_speed = min(4.0, self.game_speed + 0.5)
        
        elif button_name == 'speed_down':
            self.game_speed = max(0.5, self.game_speed - 0.5)
        
        elif button_name == 'show_stats':
            self.show_graphs = not self.show_graphs
            self.buttons['show_stats'].active = self.show_graphs

    def _update_stats_history(self):
        stats = self.model.get_statistics()
        self.stats_history['happiness'].append(stats['social_metrics']['average_happiness'])
        self.stats_history['wealth'].append(stats['economy']['total_wealth'])
        self.stats_history['population'].append(stats['population'])
        
        for resource in self.stats_history['resources']:
            self.stats_history['resources'][resource].append(
                stats['economy']['resources'][resource]
            )
    
    def _update_model(self):
        if not self.paused:
            # ... существующий код обновления ...
            self._update_stats_history()
    
    def run(self):
        """Главный игровой цикл"""
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            self._handle_camera_movement()
            self._update_model()  # Обновление модели
            self.draw()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = VillageGame()
    game.run() 