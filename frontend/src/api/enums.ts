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
};
