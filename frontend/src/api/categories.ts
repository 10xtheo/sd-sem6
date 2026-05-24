import client from './client';
import type { Category } from '../types';

export type TreeCatItem = { type: 'category'; id: number; name: string; level: number; parent_id: number | null };
export type TreePosItem = {
  type: 'position'; id: number; name: string; category_id: number; level: number;
  parameters: Array<{ parameter_id: number; short_name: string | null; val_real: number | null; val_int: number | null; val_str: string | null; val_dt: string | null; enum_val_id: number | null }>;
};
export type TreeResponse = { items: Array<TreeCatItem | TreePosItem> };

export const categoriesApi = {
  getAll: () => client.get<Category[]>('/categories').then(r => r.data),

  /** GET /categories/tree — returns categories+positions with levels, supports param filters */
  getTree: (params?: Record<string, string | number>) =>
    client.get<TreeResponse>('/categories/tree', { params }).then(r => r.data),

  getById: (id: number) =>
    client.get<Category>(`/categories/${id}`).then(r => r.data),

  getChildren: (id: number) =>
    client.get<Category[]>(`/categories/${id}/children`).then(r => r.data),

  getDescendants: (id: number) =>
    client.get<Category[]>(`/categories/${id}/descendants`).then(r => r.data),

  /** GET /categories/{id}/parents — returns ancestor chain root→parent */
  getParents: (id: number) =>
    client.get<{ id: number; name: string; parent_id: number | null }[]>(`/categories/${id}/parents`).then(r => r.data),

  create: (data: { name: string; parent_id: number | null }) =>
    client.post<Category>('/categories', data).then(r => r.data),

  update: (id: number, data: { name: string }) =>
    client.patch<Category>(`/categories/${id}`, data).then(r => r.data),

  move: (id: number, new_parent_id: number | null) =>
    client.patch<Category>(`/categories/${id}/move`, { new_parent_id }).then(r => r.data),

  delete: (id: number, cascade = false) =>
    client.delete(`/categories/${id}`, { params: { cascade } }),
};
