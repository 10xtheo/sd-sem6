from models import Category, Position
from database import init_db

from .helpers import clear_screen, print_header, print_menu_item, wait_for_enter, print_tree

def settings_menu(session, cat_repo, pos_repo):
    """Меню настроек"""
    while True:
        clear_screen()
        print_header("НАСТРОЙКИ")
        
        print_menu_item(1, "Инициализировать базу данных")
        print_menu_item(2, "Загрузить тестовые данные")
        print_menu_item(3, "Очистить базу данных")
        print_menu_item(4, "Показать структуру БД")
        print_menu_item(0, "Вернуться в главное меню")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "1":
            clear_screen()
            print_header("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
            
            confirm = input("Это создаст новые таблицы. Продолжить? (y/n): ").strip().lower()
            if confirm == 'y':
                init_db()
                print("\n✅ База данных инициализирована")
            else:
                print("\nОперация отменена")
            
            wait_for_enter()
        
        elif choice == "2":
            clear_screen()
            print_header("ЗАГРУЗКА ТЕСТОВЫХ ДАННЫХ")
            # todo place test data to separate .json - parse it here
            confirm = input("Это добавит тестовые данные. Продолжить? (y/n): ").strip().lower()
            if confirm == 'y':
                try:
                    # Очистка перед загрузкой
                    session.query(Position).delete()
                    session.query(Category).delete()
                    session.commit()
                    
                    # Создание тестовых категорий
                    food = cat_repo.add_category("Продукты питания")
                    meat = cat_repo.add_category("Мясо", food.id)
                    veggies = cat_repo.add_category("Овощи", food.id)
                    fruits = cat_repo.add_category("Фрукты", food.id)
                    drinks = cat_repo.add_category("Напитки", food.id)
                    dairy = cat_repo.add_category("Молочные продукты", food.id)
                    
                    # Подкатегории
                    beef = cat_repo.add_category("Говядина", meat.id)
                    pork = cat_repo.add_category("Свинина", meat.id)
                    chicken = cat_repo.add_category("Курица", meat.id)
                    
                    root_veggies = cat_repo.add_category("Корнеплоды", veggies.id)
                    
                    # Создание тестовых позиций
                    positions = [
                        # Мясо
                        (meat.id, "Стейк рибай", 300, 350, 27, 25, 0, False, True),
                        (meat.id, "Куриное филе", 200, 165, 31, 3.6, 0, False, False),
                        (beef.id, "Говядина тушеная", 250, 250, 26, 17, 0, False, True),
                        (pork.id, "Свинина жареная", 200, 242, 27, 14, 0, False, True),
                        (chicken.id, "Куриная грудка", 200, 165, 31, 3.6, 0, False, False),
                        
                        # Овощи
                        (veggies.id, "Помидор", 150, 18, 0.9, 0.2, 3.9, False, False),
                        (veggies.id, "Огурец", 150, 15, 0.8, 0.1, 3.0, False, False),
                        (root_veggies.id, "Картофель", 200, 77, 2.0, 0.1, 17, False, True),
                        (root_veggies.id, "Морковь", 150, 41, 0.9, 0.2, 10, False, False),
                        
                        # Фрукты
                        (fruits.id, "Яблоко", 180, 95, 0.5, 0.3, 25, False, False),
                        (fruits.id, "Банан", 150, 105, 1.3, 0.4, 27, False, False),
                        (fruits.id, "Апельсин", 200, 62, 1.2, 0.2, 15, False, False),
                        
                        # Напитки
                        (drinks.id, "Вода", 500, 0, 0, 0, 0, True, False),
                        (drinks.id, "Кофе", 300, 2, 0.3, 0, 0, True, True),
                        (drinks.id, "Чай", 300, 1, 0, 0, 0, True, True),
                        (drinks.id, "Сок апельсиновый", 250, 110, 1.5, 0.5, 26, True, False),
                        
                        # Молочные продукты
                        (dairy.id, "Молоко", 200, 103, 6.4, 3.6, 4.8, True, False),
                        (dairy.id, "Йогурт", 150, 120, 5.0, 3.0, 18, False, False),
                        (dairy.id, "Сыр", 50, 200, 12, 16, 0, False, False),
                    ]
                    
                    for pos_data in positions:
                        pos_repo.add_position(
                            category_id=pos_data[0],
                            name=pos_data[1],
                            weight=pos_data[2],
                            calories=pos_data[3],
                            protein=pos_data[4],
                            fat=pos_data[5],
                            carbs=pos_data[6],
                            is_liquid=pos_data[7],
                            is_hot=pos_data[8]
                        )
                    
                    print("\n✅ Тестовые данные загружены!")
                    print_tree(session)
                    
                except Exception as e:
                    print(f"\n❌ Ошибка: {e}")
                    session.rollback()
            else:
                print("\nОперация отменена")
            
            wait_for_enter()
        
        elif choice == "3":
            clear_screen()
            print_header("ОЧИСТКА БАЗЫ ДАННЫХ")
            
            print("ВНИМАНИЕ! Это удалит ВСЕ данные!")
            confirm = input("Введите 'DELETE ALL' для подтверждения: ").strip()
            
            if confirm == 'DELETE ALL':
                session.query(Position).delete()
                session.query(Category).delete()
                session.commit()
                print("\n✅ База данных очищена")
            else:
                print("\nОперация отменена")
            
            wait_for_enter()
        
        elif choice == "4":
            clear_screen()
            print_header("СТРУКТУРА БАЗЫ ДАННЫХ")
            
            print("📁 Таблица categories:")
            print("  • id (INTEGER, PRIMARY KEY)")
            print("  • name (VARCHAR(255), NOT NULL)")
            print("  • parent_id (INTEGER, FOREIGN KEY → categories.id)")
            print("  • Индекс: ix_categories_parent_id")
            
            print("\n📄 Таблица positions:")
            print("  • id (INTEGER, PRIMARY KEY)")
            print("  • category_id (INTEGER, FOREIGN KEY → categories.id, NOT NULL)")
            print("  • name (VARCHAR(255), NOT NULL)")
            print("  • weight (SMALLINT)")
            print("  • calories (SMALLINT)")
            print("  • protein (SMALLINT)")
            print("  • fat (SMALLINT)")
            print("  • carbs (SMALLINT)")
            print("  • is_liquid (BOOLEAN, default=False)")
            print("  • is_hot (BOOLEAN, default=False)")
            print("  • Индекс: ix_positions_category_id")
            
            wait_for_enter()
        
        elif choice == "0":
            break
