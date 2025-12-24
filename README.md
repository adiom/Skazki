# Симуляция деревни

Агентная модель жизни деревни + игровая демка на pygame. Есть ядро симуляции (Mesa/NetworkX), генерация статистики и графиков, а также заготовка для ИИ-советника (LLM). Деревня пока не бастует - но это временно.

## Что внутри

- **Ядро симуляции**: жители с демографией, личностью и навыками; социальная сеть; базовая экономика и метрики (wealth/happiness).
- **Запуск симуляции**: сбор статистики, выгрузка CSV/JSON, генерация PNG-графиков.
- **Игровая демка**: карта, панель управления, мини-карта, отображение объектов и жителей.
- **ИИ-модуль**: подготовлен контроллер для запросов к LLM и логирование ответов.

## Быстрый старт

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## Запуск

### Симуляция (пакет)

```bash
python -m village_simulation.src.run_simulation
```

По умолчанию: 200 жителей, 10 лет, сохранение каждые 7 дней.  
Параметры можно менять через вызов `run_simulation(...)` в Python:

```python
from village_simulation.src.run_simulation import run_simulation

run_simulation(num_agents=100, years=2, save_frequency=1, output_dir="data/simulation_results")
```

### Игровая демка (pygame)

```bash
python village_simulation/run_game.py
```

Демо использует ту же модель, отображает карту и UI, а также пишет логи в `logs/`.

## Результаты и логи

- `data/simulation_results/`
  - `daily_statistics.csv` (день, дата, население, wealth, happiness)
  - `raw_results.json` (полная структура результатов)
  - `population_dynamics.png`, `wealth_dynamics.png`, `happiness_dynamics.png`
- `logs/`
  - `village_simulation_YYYYMMDD_HHMMSS.log`
  - `ai_debug_YYYYMMDD_HHMMSS.log`

Папка `data/` в корне уже содержит пример результатов и будет перезаписываться при запуске симуляции.

## ИИ-конфигурация (.env)

Файл `.env` читается при запуске игры. Доступные переменные:

```
AI_API_TYPE=openrouter | lmstudio | vercel
OPENROUTER_API_KEY=...
VERCEL_AI_API_KEY=...
```

Для `lmstudio` ожидается локальный сервер по адресу `http://localhost:1234`.  
Переменная `AI_MODEL` есть в `.env`, но сейчас не используется - модель захардкожена в `village_simulation/ai/ai_controller.py`.

## Структура проекта

```
village_simulation/
├── src/          # ядро симуляции (агенты, модель, runner)
├── game/         # игровая демо-оболочка (pygame)
├── ai/           # ИИ-интеграции
├── data/         # зарезервировано под данные внутри пакета
├── docs/         # документация (пока пусто)
├── notebooks/    # анализ (пока пусто)
└── tests/        # тесты (пока пусто)

data/             # результаты симуляции по умолчанию
logs/             # runtime-логи (не коммитить)
```

## Тесты

```bash
pytest
```

Папка `village_simulation/tests` есть, но тестов пока нет.

## Состояние проекта и ограничения

- Логика потребностей/планирования/взаимодействий у агентов пока в виде заглушек.
- Экономика и недельный/месячный анализ не детализированы (TODO в коде).
- В игре нет логики строительства и применения ИИ-действий.
- В игровом цикле шаг модели не обновляется (пока нет вызова `VillageModel.step()`).
- Для ИИ-контроллера используется `requests`, но зависимости в `requirements.txt` пока нет.
