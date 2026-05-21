import client from './client';
import type { Position, PositionWithParameters } from '../types';

export const positionsApi = {
  getAll: (params?: { category_id?: number; search?: string }) =>
    client.get<Position[]>('/positions', { params }).then(r => r.data),

  getById: (id: number) => client.get<Position>(`/positions/${id}`).then(r => r.data),

  getFull: (id: number) =>
    client.get<PositionWithParameters>(`/positions/${id}/full`).then(r => r.data),

  getParents: (id: number) => client.get(`/positions/${id}/parents`).then(r => r.data),

  create: (data: { category_id: number; name: string }) =>
    client.post<Position>('/positions', data).then(r => r.data),

  update: (id: number, data: { name: string }) =>
    client.patch<Position>(`/positions/${id}`, data).then(r => r.data),

  move: (id: number, new_category_id: number) =>
    client.patch<Position>(`/positions/${id}/move`, { new_category_id }).then(r => r.data),

  delete: (id: number) => client.delete(`/positions/${id}`),
};
