export interface Category {
  id: number;
  name: string;
  parent_id: number | null;
}

export interface CategoryTreeNode {
  type: string;
  id: number;
  name: string;
  level: number;
}

export interface TreeNode extends Category {
  children: TreeNode[];
}

export interface Position {
  id: number;
  category_id: number;
  name: string;
}

export interface Unit {
  id: number;
  code: string;
  name: string;
  symbol: string;
}

export interface EnumType {
  id: number;
  name: string;
  code: string;
}

export interface EnumValue {
  id: number;
  enum_type_id: number;
  order_number: number;
  name: string;
  code: string | null;
  numeric_value: number | null;
  unit_id: number | null;
}

export interface Parameter {
  id: number;
  short_name: string;
  name: string;
  param_type_id: number;
  enum_type_id: number | null;
  unit_id: number | null;
}

export interface ParameterInfo {
  id: number;
  short_name: string;
  name: string;
  paramType: EnumValue;
  enumType: EnumType | null;
  unit: Unit | null;
}

export interface ParameterValue {
  parameter: ParameterInfo;
  val_real: number | null;
  val_int: number | null;
  val_str: string | null;
  val_dt: string | null;
  enum_value: EnumValue | null;
}

export interface CategoryParameter {
  category_id: number;
  parameter_id: number;
  order_num: number;
  min_val: number | null;
  max_val: number | null;
  parameter: Parameter | null;
}

export interface PositionWithParameters {
  position: Position;
  position_parameters: ParameterValue[];
}

export const PARAM_TYPE_CODES = [
  { code: 'real', label: 'Вещественное' },
  { code: 'integer', label: 'Целое' },
  { code: 'string', label: 'Строка' },
  { code: 'datetime', label: 'Дата/время' },
  { code: 'enum', label: 'Перечисление' },
] as const;
