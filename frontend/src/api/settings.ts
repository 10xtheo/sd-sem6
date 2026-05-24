import client from './client';

export const settingsApi = {
  seed:  () => client.post<{ detail: string }>('/settings/seed').then(r => r.data),
  clear: () => client.post<{ detail: string }>('/settings/clear').then(r => r.data),
};
