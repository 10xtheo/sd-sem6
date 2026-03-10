from repository.category_repository import CategoryRepository
from repository.position_repository import PositionRepository
from database import get_session

from .helpers import clear_screen, print_header, print_menu_item
from .settings_menu import settings_menu
from .category_menu import category_menu
from .position_menu import position_menu
from .search_menu import search_menu
from .stats_menu import stats_menu


def main_menu():
    session = get_session()
    cat_repo = CategoryRepository(session)
    pos_repo = PositionRepository(session)
    
    while True:
        clear_screen()
        print_header("СИСТЕМА УПРАВЛЕНИЯ КЛАССИФИКАТОРОМ ПРОДУКТОВ")
        
        print_menu_item(1, "Операции с категориями", "Добавление, перемещение, удаление категорий")
        print_menu_item(2, "Операции с позициями", "Добавление, редактирование, перемещение позиций")
        print_menu_item(3, "Поиск и просмотр", "Просмотр дерева, поиск по названию")
        print_menu_item(4, "Статистика и анализ", "Пищевая ценность, фильтры")
        print_menu_item(5, "Настройки", "Инициализация БД, загрузка тестовых данных")
        print_menu_item(0, "Выход", "Завершение работы")
        
        choice = input("\nВаш выбор: ").strip()
        if choice == "1":
            category_menu(session, cat_repo)
        elif choice == "2":
            position_menu(session, cat_repo, pos_repo)
        elif choice == "3":
            search_menu(session, cat_repo, pos_repo)
        elif choice == "4":
            stats_menu(session, cat_repo, pos_repo)
        elif choice == "5":
            settings_menu(session, cat_repo, pos_repo)
        elif choice == "0":
            print("\nДо свидания!")
            session.close()
            break
