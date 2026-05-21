import client from './client';
import type { CategoryParameter } from '../types';

export const categoryParametersApi = {
  getByCategoryId: (categoryId: number) =>
    client.get<CategoryParameter[]>(`/category-parameters/category/${categoryId}`).then(r => r.data),

  add: (data: {
    category_id: number;
    parameter_id: number;
    order_num?: number;
    min_val?: number | null;
    max_val?: number | null;
  }) => client.post('/category-parameters', data).then(r => r.data),

  remove: (categoryId: number, parameterId: number) =>
    client.delete(`/category-parameters/${categoryId}/parameters/${parameterId}`),
};
