import client from './client';
import type { Category } from '../types';

export const categoriesApi = {
  getAll: () => client.get<Category[]>('/categories').then(r => r.data),

  getTree: (start_id?: number) =>
    client.get('/categories/tree', { params: start_id ? { start_id } : {} }).then(r => r.data),

  getById: (id: number) => client.get<Category>(`/categories/${id}`).then(r => r.data),

  getChildren: (id: number) =>
    client.get<Category[]>(`/categories/${id}/children`).then(r => r.data),

  getDescendants: (id: number) =>
    client.get<Category[]>(`/categories/${id}/descendants`).then(r => r.data),

  create: (data: { name: string; parent_id: number | null }) =>
    client.post<Category>('/categories', data).then(r => r.data),

  update: (id: number, data: { name: string }) =>
    client.patch<Category>(`/categories/${id}`, data).then(r => r.data),

  move: (id: number, new_parent_id: number | null) =>
    client.patch<Category>(`/categories/${id}/move`, { new_parent_id }).then(r => r.data),

  delete: (id: number, cascade = false) =>
    client.delete(`/categories/${id}`, { params: { cascade } }),
};
