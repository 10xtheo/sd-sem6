import client from './client';

export interface StatsSummary {
  categories_total: number;
  categories_root: number;
  positions_total: number;
}

export interface StatsByCategory {
  id: number;
  name: string;
  children_count: number;
  positions_count: number;
}

export interface IntegrityIssue {
  type: string;
  category_id?: number | null;
  position_id?: number | null;
  parent_id?: number | null;
}

export interface IntegrityReport {
  ok: boolean;
  issues: IntegrityIssue[];
}

export const statsApi = {
  getSummary: () => client.get<StatsSummary>('/stats/summary').then(r => r.data),
  getByCategory: () => client.get<StatsByCategory[]>('/stats/by-category').then(r => r.data),
  getIntegrity: () => client.get<IntegrityReport>('/stats/integrity').then(r => r.data),
};
