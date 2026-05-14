from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, text

from models.category import Category
from models.category_parameter import CategoryParameter
from models.parameter import Parameter


class CategoryParameterRepository:
    def __init__(self, session: Session):
        self.session = session
    # Процедура ADD_PARAMETER_CLASS БД
    def add_to_category(self, category_id: int, parameter_id: int,
                        order_num: int = 0, min_val: Optional[float] = None,
                        max_val: Optional[float] = None) -> None:
        """Аналог add_parameter_to_category() — добавляет параметр категории и всем её потомкам"""
        
        # 1. Upsert для самой категории
        self.session.merge(CategoryParameter(
            category_id=category_id,
            parameter_id=parameter_id,
            order_num=order_num,
            min_val=min_val,
            max_val=max_val
        ))

        # 2. Получаем всех потомков
        descendant_ids = self._get_descendant_ids(category_id)
        
        if descendant_ids:
            # 3. Создаём объекты только для тех, кого ещё нет
            existing = {
                cp.category_id 
                for cp in self.session.query(CategoryParameter.category_id)
                .filter(
                    CategoryParameter.category_id.in_(descendant_ids),
                    CategoryParameter.parameter_id == parameter_id
                )
                .all()
            }

            to_add = [
                CategoryParameter(
                    category_id=did,
                    parameter_id=parameter_id,
                    order_num=order_num,
                    min_val=min_val,
                    max_val=max_val
                )
                for did in descendant_ids
                if did not in existing
            ]

            # 4. Массовое добавление
            if to_add:
                self.session.bulk_save_objects(to_add)

        self.session.commit()

    # Процедура FIND_PAR_CLASS бд
    def get_for_category(self, category_id: int):
        """Аналог find_par_category()"""
        stmt = (
            select(CategoryParameter)
            .where(CategoryParameter.category_id == category_id)
            .order_by(CategoryParameter.order_num)
        )

        return self.session.scalars(stmt).all()
    
    def _get_descendant_ids(self, category_id: int) -> List[int]:
        """Рекурсивно получает ID всех дочерних категорий"""
        descendant_ids = []
        children = self.session.query(Category).filter(
            Category.parent_id == category_id
        ).all()
        
        for child in children:
            descendant_ids.append(child.id)
            descendant_ids.extend(self._get_descendant_ids(child.id))
        
        return descendant_ids
    
    def parameter_exists_in_category(self, category_id: int, parameter_id: int) -> bool:
        """Проверяет, существует ли параметр у категории"""
        return self.session.query(CategoryParameter).filter(
            CategoryParameter.category_id == category_id,
            CategoryParameter.parameter_id == parameter_id
        ).first() is not None

    def delete_from_category(self, category_id: int, parameter_id: int) -> int:
        """
        Удаляет параметр у категории и всех её потомков (каскадно).
        Возвращает количество удаленных записей.
        """
        # Получаем все дочерние категории
        descendant_ids = self._get_descendant_ids(category_id)
        all_category_ids = [category_id] + descendant_ids
        
        # Удаляем параметр у всех найденных категорий
        deleted_count = self.session.query(CategoryParameter).filter(
            CategoryParameter.category_id.in_(all_category_ids),
            CategoryParameter.parameter_id == parameter_id
        ).delete(synchronize_session=False)
        
        self.session.commit()
        return deleted_count
    