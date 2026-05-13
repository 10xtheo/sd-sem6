from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.parameter import Parameter
from models.enum_value import EnumValue
from models.enum_type import EnumType


class ParameterRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, short_name: str, name: str, param_type_code: str,
            enum_type_id: Optional[int] = None, unit_id: Optional[int] = None) -> Parameter:
        
        result = self.session.execute(
            select(EnumValue.id)
            .join(EnumType)
            .where(
                EnumValue.code == param_type_code,
                EnumType.code == 'param_type'
            )
        ).first()

        if not result:
            raise ValueError(f"Неизвестный тип параметра: {param_type_code}")

        param_type_id = result[0]

        param = Parameter(
            short_name=short_name,
            name=name,
            param_type_id=param_type_id,
            enum_type_id=enum_type_id,
            unit_id=unit_id
        )
        self.session.add(param)
        self.session.commit()
        self.session.refresh(param)

        return param
    

    def get_all(self) -> List[Parameter]:
        return self.session.query(Parameter).all()

    def get_by_id(self, param_id: int) -> Optional[Parameter]:
        return self.session.get(Parameter, param_id)

    def get_by_short_name(self, short_name: str) -> Optional[Parameter]:
        return self.session.query(Parameter).filter_by(short_name=short_name).first()
    
    def delete_parameter(self, parameter_id: int) -> None:
        parameter = self.get_by_id(parameter_id)
        if not parameter:
            raise ValueError(f"Параметр с ID {parameter_id} не найден")
        
        self.session.delete(parameter)
        self.session.commit()
