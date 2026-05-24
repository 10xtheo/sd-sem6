import client from './client';
import type { EnumType, EnumValue } from '../types';

export const enumsApi = {
  getTypes: () => client.get<EnumType[]>('/enum/types').then(r => r.data),

  getType: (id: number) => client.get<EnumType>(`/enum/types/${id}`).then(r => r.data),

  getTypeValues: (id: number, desc = false) =>
    client.get<EnumValue[]>(`/enum/types/${id}/values`, { params: { desc } }).then(r => r.data),

  createType: (data: { name: string; code: string }) =>
    client.post<EnumType>('/enum/types', data).then(r => r.data),

  updateType: (id: number, data: Partial<{ name: string; code: string }>) =>
    client.patch<EnumType>(`/enum/types/${id}`, data).then(r => r.data),

  deleteType: (id: number) => client.delete(`/enum/types/${id}`),

  getValues: () => client.get<EnumValue[]>('/enum/values').then(r => r.data),

  getValue: (id: number) => client.get<EnumValue>(`/enum/values/${id}`).then(r => r.data),

  createValue: (data: {
    enum_type_id: number;
    order_number: number;
    name: string;
    code?: string | null;
    numeric_value?: number | null;
    unit_id?: number | null;
  }) => client.post<EnumValue>('/enum/values', data).then(r => r.data),

  updateValue: (id: number, data: Partial<Omit<EnumValue, 'id' | 'enum_type_id'>>) =>
    client.patch<EnumValue>(`/enum/values/${id}`, data).then(r => r.data),

  deleteValue: (id: number) => client.delete(`/enum/values/${id}`),

  /** POST /enum/validate — check if a value string belongs to a given type (by code) */
  validate: (type_code: string, value: string) =>
    client.post<{ valid: boolean; id: number; name: string }>('/enum/validate', { type_code, value })
      .then(r => r.data),
};
