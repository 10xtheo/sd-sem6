import client from './client';
import type { Unit } from '../types';

export const unitsApi = {
  getAll: () => client.get<Unit[]>('/units').then(r => r.data),

  getById: (id: number) => client.get<Unit>(`/units/${id}`).then(r => r.data),

  create: (data: { code: string; name: string; symbol: string }) =>
    client.post<Unit>('/units', data).then(r => r.data),

  update: (id: number, data: Partial<{ code: string; name: string; symbol: string }>) =>
    client.patch<Unit>(`/units/${id}`, data).then(r => r.data),

  delete: (id: number) => client.delete(`/units/${id}`),
};
