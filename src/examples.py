"""
ORM Quick Start для каталога продуктов

Соответствует диаграмме:
- Категория (id, название, parent_id)
- Позиция (id, category_id, название, вес, калорийность, белки, жиры, углеводы, жидкое, горячее)
"""

from database import init_db, get_session

from repository.category_repository import CategoryRepository
from repository.position_repository import PositionRepository

def main():
    # 1. Инициализация базы данных
    print("Инициализация базы данных...")
    init_db()
    
    # 2. Создание сессии
    session = get_session()
    cat_repo = CategoryRepository(session)
    pos_repo = PositionRepository(session)
    
    # 3. Создание категорий
    print("\n1. Создание категорий...")
    food = cat_repo.add_category("Продукты питания")
    meat = cat_repo.add_category("Мясо", food.id)
    veggies = cat_repo.add_category("Овощи", food.id)
    drinks = cat_repo.add_category("Напитки", food.id)
    
    print(f"   Созданы категории: {food.name}, {meat.name}, {veggies.name}, {drinks.name}")
    
    # 4. Создание позиций
    print("\n2. Создание позиций...")
    
    # Мясо
    beef = pos_repo.add_position(
        category_id=meat.id,
        name="Говядина",
        weight=250,
        calories=250,
        protein=26,
        fat=17,
        carbs=0,
        is_hot=False
    )
    
    pork = pos_repo.add_position(
        category_id=meat.id,
        name="Свинина",
        weight=200,
        calories=242,
        protein=27,
        fat=14,
        carbs=0,
        is_hot=False
    )
    
    # Овощи
    potato = pos_repo.add_position(
        category_id=veggies.id,
        name="Картофель",
        weight=200,
        calories=77,
        protein=2,
        fat=1,
        carbs=170,
        is_hot=False
    )
    
    tomato = pos_repo.add_position(
        category_id=veggies.id,
        name="Помидор",
        weight=150,
        calories=18,
        protein=9,
        fat=2,
        carbs=39,
        is_hot=False
    )
    
    # Напитки
    water = pos_repo.add_position(
        category_id=drinks.id,
        name="Вода",
        weight=500,
        calories=0,
        protein=0,
        fat=0,
        carbs=0,
        is_liquid=True,
        is_hot=False
    )
    
    coffee = pos_repo.add_position(
        category_id=drinks.id,
        name="Кофе",
        weight=300,
        calories=2,
        protein=300,
        fat=0,
        carbs=0,
        is_liquid=True,
        is_hot=True
    )
    
    print(f"   Создано 6 позиций")
    
    # 5. Получение дерева категорий
    print("\n3. Дерево категорий с позициями:")
    tree = cat_repo.get_category_tree()
    
    def print_tree(node, level=0):
        indent = "  " * level
        print(f"{indent}📁 {node['name']} (id: {node['id']})")
        for pos in node['positions']:
            liquid = "💧" if pos['is_liquid'] else ""
            hot = "🔥" if pos['is_hot'] else ""
            print(f"{indent}  📄 {pos['name']}{liquid}{hot} - {pos['weight']}г, {pos['calories']}ккал")
        for child in node['children']:
            print_tree(child, level + 1)
    
    for root in tree:
        print_tree(root)
    
    # 6. Поиск позиций
    print("\n4. Поиск позиций по названию 'кар':")
    found = pos_repo.search_positions("кар")
    for pos in found:
        print(f"   • {pos.name} (категория: {pos.category.name})")
    
    # 7. Фильтрация позиций
    print("\n5. Горячие напитки:")
    hot_drinks = pos_repo.get_filtered_positions(
        is_hot=True,
        is_liquid=True
    )
    for pos in hot_drinks:
        print(f"   • {pos.name}")
    
    # 8. Перемещение позиции
    print("\n6. Перемещение картофеля из 'Овощи' в новую категорию...")
    # Создаем подкатегорию "Корнеплоды" в "Овощи"
    root_veggies = cat_repo.add_category("Корнеплоды", veggies.id)
    pos_repo.move_position(potato.id, root_veggies.id)
    print(f"   Картофель перемещен в '{root_veggies.name}'")
    
    # 9. Обновление дерева
    print("\n7. Обновленное дерево:")
    tree = cat_repo.get_category_tree()
    for root in tree:
        print_tree(root)
    
    session.close()

if __name__ == "__main__":
    main()
