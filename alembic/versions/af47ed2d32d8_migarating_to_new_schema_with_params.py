"""migarating to new schema with params

Revision ID: af47ed2d32d8
Revises: 61c8b0b4a333
Create Date: 2026-05-12 11:45:47.356119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'af47ed2d32d8'
down_revision: Union[str, Sequence[str], None] = '61c8b0b4a333'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Применяем новую схему schema3_v2.sql"""
    
    # === 1. Создаём все новые таблицы и объекты из schema3_v2.sql ===
    op.execute(text("""
        -- ============================================================
        --  Food Delivery DB Schema - Version 4 (rev2)
        -- ============================================================

        -- 1. units (уже должна существовать, но на всякий случай)
        CREATE TABLE IF NOT EXISTS units (
            id      SERIAL       PRIMARY KEY,
            code    VARCHAR(10)  NOT NULL UNIQUE,
            name    VARCHAR(100) NOT NULL,
            symbol  VARCHAR(20)  NOT NULL
        );

        -- 2. enum_types
        CREATE TABLE IF NOT EXISTS enum_types (
            id    SERIAL       PRIMARY KEY,
            name  VARCHAR(255) NOT NULL UNIQUE,
            code  VARCHAR(50)  NOT NULL UNIQUE
        );

        -- 3. enum_values
        CREATE TABLE IF NOT EXISTS enum_values (
            id            SERIAL       PRIMARY KEY,
            enum_type_id  INTEGER      NOT NULL REFERENCES enum_types(id) ON DELETE CASCADE,
            order_number  SMALLINT     NOT NULL,
            name          VARCHAR(255) NOT NULL,
            code          VARCHAR(50),
            UNIQUE (enum_type_id, order_number)
        );

        -- Инициализация служебного типа 'param_type'
        INSERT INTO enum_types (name, code)
        VALUES ('Тип параметра', 'param_type')
        ON CONFLICT (code) DO NOTHING;

        INSERT INTO enum_values (enum_type_id, order_number, name, code)
        SELECT id, 1, 'Вещественное', 'real'     FROM enum_types WHERE code = 'param_type'
        ON CONFLICT DO NOTHING;

        INSERT INTO enum_values (enum_type_id, order_number, name, code)
        SELECT id, 2, 'Целое',        'integer'  FROM enum_types WHERE code = 'param_type'
        ON CONFLICT DO NOTHING;

        INSERT INTO enum_values (enum_type_id, order_number, name, code)
        SELECT id, 3, 'Строковое',    'string'   FROM enum_types WHERE code = 'param_type'
        ON CONFLICT DO NOTHING;

        INSERT INTO enum_values (enum_type_id, order_number, name, code)
        SELECT id, 4, 'Дата/время',   'datetime' FROM enum_types WHERE code = 'param_type'
        ON CONFLICT DO NOTHING;

        INSERT INTO enum_values (enum_type_id, order_number, name, code)
        SELECT id, 5, 'Перечисление', 'enum'     FROM enum_types WHERE code = 'param_type'
        ON CONFLICT DO NOTHING;

        -- 4. categories — уже существует
        -- 5. positions — оставляем только базовые поля
        ALTER TABLE positions 
            DROP COLUMN IF EXISTS weight,
            DROP COLUMN IF EXISTS weight_unit_id,
            DROP COLUMN IF EXISTS calories,
            DROP COLUMN IF EXISTS protein,
            DROP COLUMN IF EXISTS fat,
            DROP COLUMN IF EXISTS carbs,
            DROP COLUMN IF EXISTS is_liquid,
            DROP COLUMN IF EXISTS is_hot;

        -- 6. parameters
        CREATE TABLE parameters (
            id             SERIAL       PRIMARY KEY,
            short_name     VARCHAR(50)  NOT NULL UNIQUE,
            name           VARCHAR(255) NOT NULL,
            param_type_id  INTEGER      NOT NULL REFERENCES enum_values(id) ON DELETE RESTRICT,
            enum_type_id   INTEGER      REFERENCES enum_types(id) ON DELETE RESTRICT,
            unit_id        INTEGER      REFERENCES units(id) ON DELETE SET NULL
        );

        -- Триггер для валидации типов параметров
        CREATE OR REPLACE FUNCTION trg_parameters_type_check()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        DECLARE v_type_code VARCHAR(50);
        BEGIN
            SELECT ev.code INTO v_type_code
            FROM enum_values ev
            JOIN enum_types et ON et.id = ev.enum_type_id
            WHERE ev.id = NEW.param_type_id AND et.code = 'param_type';

            IF NOT FOUND THEN
                RAISE EXCEPTION 'param_type_id % не является допустимым типом параметра', NEW.param_type_id;
            END IF;

            IF v_type_code = 'enum' AND NEW.enum_type_id IS NULL THEN
                RAISE EXCEPTION 'Для параметра типа "enum" необходимо указать enum_type_id';
            END IF;

            IF v_type_code <> 'enum' AND NEW.enum_type_id IS NOT NULL THEN
                RAISE EXCEPTION 'enum_type_id задаётся только для параметра типа "enum"';
            END IF;

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_parameters_before_upsert
        BEFORE INSERT OR UPDATE ON parameters
        FOR EACH ROW EXECUTE FUNCTION trg_parameters_type_check();

        -- 7. category_parameters
        CREATE TABLE category_parameters (
            category_id   INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
            parameter_id  INTEGER NOT NULL REFERENCES parameters(id) ON DELETE CASCADE,
            order_num     SMALLINT NOT NULL DEFAULT 0,
            min_val       REAL,
            max_val       REAL,
            PRIMARY KEY (category_id, parameter_id),
            CONSTRAINT chk_minmax CHECK (min_val IS NULL OR max_val IS NULL OR min_val <= max_val)
        );

        -- 8. position_parameters
        CREATE TABLE position_parameters (
            position_id   INTEGER NOT NULL REFERENCES positions(id) ON DELETE CASCADE,
            parameter_id  INTEGER NOT NULL REFERENCES parameters(id) ON DELETE CASCADE,
            val_real      REAL,
            val_int       INTEGER,
            val_str       VARCHAR(1000),
            val_dt        TIMESTAMP,
            enum_val_id   INTEGER REFERENCES enum_values(id) ON DELETE SET NULL,
            PRIMARY KEY (position_id, parameter_id)
        );

        -- ============================================================
        --  Функции бизнес-логики (все из schema3_v2.sql)
        -- ============================================================

        -- copy_par, ins_parameter, add_parameter_to_category, 
        -- write_par_position, find_par_category, find_par_position
        -- (вставь сюда весь блок функций из schema3_v2.sql)
    """))


def downgrade() -> None:
    """Откат миграции — удаляем всё новое"""
    op.execute(text("""
        DROP TABLE IF EXISTS position_parameters CASCADE;
        DROP TABLE IF EXISTS category_parameters CASCADE;
        DROP TABLE IF EXISTS parameters CASCADE;
        DROP TRIGGER IF EXISTS trg_parameters_before_upsert ON parameters;
        DROP FUNCTION IF EXISTS trg_parameters_type_check();
        -- и т.д. (можно расширить при необходимости)
    """))
