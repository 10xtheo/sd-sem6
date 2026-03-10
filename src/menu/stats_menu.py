from tabulate import tabulate
from sqlalchemy import func

from models import Category, Position

from .helpers import clear_screen, print_header, print_menu_item, wait_for_enter


def stats_menu(session, cat_repo, pos_repo):
    while True:
        clear_screen()
        print_header("СТАТИСТИКА И АНАЛИЗ")
        
        print_menu_item(1, "Общая статистика")
        print_menu_item(2, "Статистика по категориям")
        print_menu_item(3, "Анализ пищевой ценности")
        print_menu_item(4, "Поиск по диапазону калорий")
        print_menu_item(5, "Проверка целостности данных")
        print_menu_item(0, "Вернуться в главное меню")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "1":
            clear_screen()
            print_header("ОБЩАЯ СТАТИСТИКА")
            
            categories_count = session.query(Category).count()
            positions_count = session.query(Position).count()
            root_categories = session.query(Category).filter(Category.parent_id.is_(None)).count()
            
            print(f"📊 Всего категорий: {categories_count}")
            print(f"📊 Корневых категорий: {root_categories}")
            print(f"📊 Всего позиций: {positions_count}")
            
            if positions_count > 0:
                avg_cal = session.query(func.avg(Position.calories)).scalar() or 0
                max_cal = session.query(func.max(Position.calories)).scalar() or 0
                liquid_count = session.query(Position).filter(Position.is_liquid == True).count()
                hot_count = session.query(Position).filter(Position.is_hot == True).count()
                
                print(f"\n📊 Средняя калорийность: {avg_cal:.1f} ккал")
                print(f"📊 Максимальная калорийность: {max_cal} ккал")
                print(f"📊 Жидких позиций: {liquid_count}")
                print(f"📊 Горячих позиций: {hot_count}")
            
            wait_for_enter()
        
        elif choice == "2":
            clear_screen()
            print_header("СТАТИСТИКА ПО КАТЕГОРИЯМ")
            
            categories = cat_repo.get_all_categories()
            if categories:
                table = []
                for cat in categories:
                    positions_count = len(pos_repo.get_positions_by_category(cat.id))
                    children_count = len(cat.get_children(session))
                    table.append([cat.id, cat.name, children_count, positions_count])
                
                print(tabulate(table, 
                              headers=["ID", "Категория", "Подкатегорий", "Позиций"], 
                              tablefmt="grid"))
            else:
                print("Категории отсутствуют")
            
            wait_for_enter()
        
        elif choice == "3":
            clear_screen()
            print_header("АНАЛИЗ ПИЩЕВОЙ ЦЕННОСТИ")
            
            # Топ по калориям
            top_calories = session.query(Position).order_by(Position.calories.desc()).limit(5).all()
            if top_calories:
                print("🏆 Топ-5 по калорийности:")
                for p in top_calories:
                    print(f"  • {p.name} - {p.calories} ккал ({p.category.name})")
            
            # Топ по белкам
            top_protein = session.query(Position).order_by(Position.protein.desc()).limit(5).all()
            if top_protein:
                print("\n🥩 Топ-5 по содержанию белка:")
                for p in top_protein:
                    print(f"  • {p.name} - {p.protein}г ({p.category.name})")
            
            wait_for_enter()
        
        elif choice == "4":
            clear_screen()
            print_header("ПОИСК ПО ДИАПАЗОНУ КАЛОРИЙ")
            
            min_cal = input("Минимальная калорийность: ").strip()
            max_cal = input("Максимальная калорийность: ").strip()
            
            min_cal = int(min_cal) if min_cal else 0
            max_cal = int(max_cal) if max_cal else 9999
            
            positions = session.query(Position).filter(
                Position.calories.between(min_cal, max_cal)
            ).order_by(Position.calories).all()
            
            if positions:
                print(f"\nПозиции с калорийностью от {min_cal} до {max_cal}:")
                table = []
                for p in positions:
                    table.append([p.name, p.calories, p.category.name])
                print(tabulate(table, headers=["Название", "Ккал", "Категория"], tablefmt="grid"))
            else:
                print("\nПозиции не найдены")
            
            wait_for_enter()
        
        elif choice == "5":
            clear_screen()
            print_header("ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ")
            
            issues = []
            
            # Проверка на циклические ссылки в категориях
            categories = cat_repo.get_all_categories()
            for cat in categories:
                # Простая проверка: если категория ссылается на себя
                if cat.parent_id == cat.id:
                    issues.append(f"❌ Категория {cat.id} ссылается сама на себя")
                
                # Проверка на существование родителя
                if cat.parent_id and not cat_repo.get_category(cat.parent_id):
                    issues.append(f"❌ Категория {cat.id} ссылается на несуществующего родителя {cat.parent_id}")
            
            # Проверка позиций
            positions = session.query(Position).all()
            for pos in positions:
                if not cat_repo.get_category(pos.category_id):
                    issues.append(f"❌ Позиция {pos.id} ссылается на несуществующую категорию {pos.category_id}")
            
            if issues:
                print("\n".join(issues))
            else:
                print("✅ Все проверки пройдены успешно")
            
            wait_for_enter()
        
        elif choice == "0":
            break
