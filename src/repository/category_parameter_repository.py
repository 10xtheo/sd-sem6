from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, text

from models.category_parameter import CategoryParameter
from models.parameter import Parameter


class CategoryParameterRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_to_category(self, category_id: int, parameter_id: int,
                        order_num: int = 0, min_val: Optional[float] = None,
                        max_val: Optional[float] = None) -> None:
        """Аналог add_parameter_to_category() — с распространением на дочерние категории"""
        # Основная категория
        cp = CategoryParameter(
            category_id=category_id,
            parameter_id=parameter_id,
            order_num=order_num,
            min_val=min_val,
            max_val=max_val
        )
        self.session.merge(cp)  # ON CONFLICT UPDATE

        # Распространение на дочерние (рекурсивно через CTE)
        self.session.execute(text("""
            INSERT INTO category_parameters (category_id, parameter_id, order_num, min_val, max_val)
            WITH RECURSIVE descendants AS (
                SELECT id FROM categories WHERE parent_id = :category_id
                UNION ALL
                SELECT c.id FROM categories c
                JOIN descendants d ON c.parent_id = d.id
            )
            SELECT d.id, :parameter_id, :order_num, :min_val, :max_val
            FROM descendants d
            ON CONFLICT (category_id, parameter_id) DO NOTHING;
        """), {
            "category_id": category_id,
            "parameter_id": parameter_id,
            "order_num": order_num,
            "min_val": min_val,
            "max_val": max_val
        })

        self.session.commit()

    def get_for_category(self, category_id: int):
        """Аналог find_par_category()"""
        stmt = (
            select(CategoryParameter)
            .where(CategoryParameter.category_id == category_id)
            .order_by(CategoryParameter.order_num)
        )

        return self.session.scalars(stmt).all()
