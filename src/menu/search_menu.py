from tabulate import tabulate

from .helpers import clear_screen, print_header, print_menu_item, wait_for_enter, print_tree


def search_menu(session, cat_repo, pos_repo):
    while True:
        clear_screen()
        print_header("ПОИСК И ПРОСМОТР")
        
        print_menu_item(1, "Показать дерево категорий")
        print_menu_item(2, "Поиск позиций по названию")
        print_menu_item(3, "Поиск позиций по категории")
        print_menu_item(4, "Поиск позиций по свойствам")
        print_menu_item(5, "Просмотр информации о категории")
        print_menu_item(0, "Вернуться в главное меню")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "1":
            clear_screen()
            print_header("ДЕРЕВО КАТЕГОРИЙ")
            print_tree(cat_repo)
            wait_for_enter()
        
        elif choice == "2":
            clear_screen()
            print_header("ПОИСК ПОЗИЦИЙ ПО НАЗВАНИЮ")
            
            query = input("Введите текст для поиска: ").strip()
            
            positions = pos_repo.search_positions(query)
            if positions:
                table = []
                for p in positions:
                    table.append([
                        p.id, p.name, p.category.name if p.category else "—",
                        p.weight or "—", p.calories or "—"
                    ])
                print(tabulate(table, 
                              headers=["ID", "Название", "Категория", "Вес", "Ккал"], 
                              tablefmt="grid"))
            else:
                print("\nПозиции не найдены")
            
            wait_for_enter()
        
        elif choice == "3":
            clear_screen()
            print_header("ПОИСК ПОЗИЦИЙ ПО КАТЕГОРИИ")
            
            # Показываем дерево
            print_tree(cat_repo)
            
            category_id = input("\nID категории: ").strip()
            if not category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            positions = pos_repo.get_positions_by_category(int(category_id))
            if positions:
                category = cat_repo.get_category(int(category_id))
                print(f"\nПозиции в категории '{category.name}':")
                table = []
                for p in positions:
                    table.append([p.id, p.name, p.weight or "—", p.calories or "—"])
                print(tabulate(table, headers=["ID", "Название", "Вес", "Ккал"], tablefmt="grid"))
            else:
                print("\nВ этой категории нет позиций")
            
            wait_for_enter()
        
        elif choice == "4":
            clear_screen()
            print_header("ПОИСК ПОЗИЦИЙ ПО СВОЙСТВАМ")
            
            print("Фильтры (Enter для пропуска):")
            is_liquid_input = input("Только жидкие? (y/n): ").strip().lower()
            is_liquid = True if is_liquid_input == 'y' else (False if is_liquid_input == 'n' else None)
            
            is_hot_input = input("Только горячие? (y/n): ").strip().lower()
            is_hot = True if is_hot_input == 'y' else (False if is_hot_input == 'n' else None)
            
            min_cal = input("Минимальная калорийность: ").strip()
            min_cal = int(min_cal) if min_cal else None
            
            max_cal = input("Максимальная калорийность: ").strip()
            max_cal = int(max_cal) if max_cal else None
            
            positions = pos_repo.get_filtered_positions(
                min_calories=min_cal,
                max_calories=max_cal,
                is_liquid=is_liquid,
                is_hot=is_hot
            )
            
            if positions:
                table = []
                for p in positions:
                    liquid = "💧" if p.is_liquid else ""
                    hot = "🔥" if p.is_hot else ""
                    table.append([
                        p.id, p.name, p.category.name if p.category else "—",
                        p.calories or "—", f"{liquid}{hot}"
                    ])
                print(tabulate(table, 
                              headers=["ID", "Название", "Категория", "Ккал", "Свойства"], 
                              tablefmt="grid"))
            else:
                print("\nПозиции не найдены")
            
            wait_for_enter()
        
        elif choice == "5":
            clear_screen()
            print_header("ИНФОРМАЦИЯ О КАТЕГОРИИ")
            
            category_id = input("ID категории: ").strip()
            if not category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            category = cat_repo.get_category(int(category_id))
            if category:
                print(f"\n📁 Категория: {category.name}")
                print(f"  ID: {category.id}")
                print(f"  Родитель: {category.parent.name if category.parent else 'Корень'}")
                
                children = category.get_children(session)
                if children:
                    print(f"  Подкатегории: {', '.join([c.name for c in children])}")
                
                positions = pos_repo.get_positions_by_category(category.id)
                if positions:
                    print(f"  Позиций: {len(positions)}")
                    
                    # Средние значения
                    if positions:
                        avg_cal = sum(p.calories or 0 for p in positions) / len(positions)
                        print(f"  Средняя калорийность: {avg_cal:.1f} ккал")
                else:
                    print("  Позиций: нет")
            else:
                print("\n❌ Категория не найдена")
            
            wait_for_enter()
        
        elif choice == "0":
            break
