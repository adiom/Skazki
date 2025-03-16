import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from .village_model import VillageModel

def run_simulation(
    output_dir: str = "data/simulation_results",
    num_agents: int = 200,
    years: int = 10,
    save_frequency: int = 7  # сохранять данные каждые N дней
):
    # Создание директории для результатов
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Инициализация модели
    model = VillageModel(
        num_agents=num_agents,
        start_date=datetime(2025, 1, 1),
        simulation_years=years
    )
    
    # Подготовка структур данных для хранения результатов
    results = {
        'daily_stats': [],
        'weekly_stats': [],
        'monthly_stats': []
    }
    
    # Запуск симуляции
    days = years * 365
    with tqdm(total=days, desc="Симуляция") as pbar:
        for day in range(days):
            # Выполнение шага симуляции
            model.step()
            
            # Сохранение результатов
            if day % save_frequency == 0:
                stats = model.get_statistics()
                results['daily_stats'].append({
                    'day': day,
                    'date': stats['date'].strftime('%Y-%m-%d'),
                    'population': stats['population'],
                    'total_wealth': stats['economy']['total_wealth'],
                    'average_happiness': stats['social_metrics']['average_happiness']
                })
            
            pbar.update(1)
    
    # Сохранение результатов
    save_results(results, output_path)
    
    # Создание визуализаций
    create_visualizations(results, output_path)
    
    return results

def save_results(results: dict, output_path: Path):
    """Сохранение результатов в файлы"""
    # Сохранение ежедневной статистики
    daily_df = pd.DataFrame(results['daily_stats'])
    daily_df.to_csv(output_path / 'daily_statistics.csv', index=False)
    
    # Сохранение сырых данных
    with open(output_path / 'raw_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

def create_visualizations(results: dict, output_path: Path):
    """Создание визуализаций результатов"""
    daily_df = pd.DataFrame(results['daily_stats'])
    
    # График населения
    plt.figure(figsize=(12, 6))
    plt.plot(daily_df['day'], daily_df['population'])
    plt.title('Динамика населения')
    plt.xlabel('День')
    plt.ylabel('Количество жителей')
    plt.savefig(output_path / 'population_dynamics.png')
    plt.close()
    
    # График благосостояния
    plt.figure(figsize=(12, 6))
    plt.plot(daily_df['day'], daily_df['total_wealth'])
    plt.title('Динамика благосостояния')
    plt.xlabel('День')
    plt.ylabel('Общее благосостояние')
    plt.savefig(output_path / 'wealth_dynamics.png')
    plt.close()
    
    # График счастья
    plt.figure(figsize=(12, 6))
    plt.plot(daily_df['day'], daily_df['average_happiness'])
    plt.title('Динамика уровня счастья')
    plt.xlabel('День')
    plt.ylabel('Средний уровень счастья')
    plt.savefig(output_path / 'happiness_dynamics.png')
    plt.close()

if __name__ == "__main__":
    run_simulation() 