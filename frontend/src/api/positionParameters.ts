import type { PositionParameter } from '../types';
import client from './client';

export interface WriteParamValues {
	val_real?: number | null;
	val_int?: number | null;
	val_str?: string | null;
	val_dt?: string | null;
	enum_val_id?: number | null;
}

export const positionParametersApi = {
	write: (positionId: number, parameterId: number, values: WriteParamValues) =>
		client
			.post(`/position-parameters/${positionId}/parameters/${parameterId}`, null, { params: values })
			.then((r) => r.data),

	getForPosition: (positionId: number) =>
		client.get<PositionParameter[]>(`/position-parameters/${positionId}`).then((r) => r.data),

	delete: (positionId: number, parameterId: number) =>
		client.delete(`/position-parameters/${positionId}/parameters/${parameterId}`),
};
