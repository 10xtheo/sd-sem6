import client from './client';
import type { Parameter } from '../types';

export interface ParameterCreate {
  short_name: string;
  name: string;
  param_type_code: string;
  enum_type_id?: number | null;
  unit_id?: number | null;
}

export const parametersApi = {
  getAll: () => client.get<Parameter[]>('/parameters').then(r => r.data),

  getById: (id: number) => client.get<Parameter>(`/parameters/${id}`).then(r => r.data),

  create: (data: ParameterCreate) =>
    client.post<Parameter>('/parameters', data).then(r => r.data),

  delete: (id: number) => client.delete(`/parameters/${id}`),
};
