import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { positionsApi } from '../api/positions';
import { enumsApi } from '../api/enums';
import { positionParametersApi } from '../api/positionParameters';
import { useToast } from '../components/Toast';
import type { CategoryParameter, ParameterValue } from '../types';
import { categoryParametersApi } from '../api/categoryParameters';

interface NewParameterState {
	parameterId: number | null;
	fieldState: FieldState;
}

const getCodeByParamTypeId = (paramTypeId: number): string => {
	switch (paramTypeId) {
		case 30: {
			return 'real';
		}
		case 31: {
			return 'integer';
		}
		case 32: {
			return 'string';
		}
		case 33: {
			return 'datetime';
		}
		case 34: {
			return 'enum';
		}
		default: {
			return 'none';
		}
	}
};
const TYPE_LABELS: Record<string, string> = {
	real: 'Вещественное',
	integer: 'Целое',
	string: 'Строка',
	datetime: 'Дата/время',
	enum: 'Перечисление',
};

function typeClass(code: string | null | undefined) {
	return `badge type-${code ?? 'gray'}`;
}

function EnumSelect({
	enumTypeId,
	value,
	onChange,
}: {
	enumTypeId: number;
	value: number | null;
	onChange: (id: number | null) => void;
}) {
	const { data: values = [] } = useQuery({
		queryKey: ['enum-values', enumTypeId],
		queryFn: () => enumsApi.getTypeValues(enumTypeId),
	});
	return (
		<select
			className="form-control"
			value={value ?? ''}
			onChange={(e) => onChange(e.target.value === '' ? null : Number(e.target.value))}
		>
			<option value="">— Не задано —</option>
			{[...values]
				.sort((a, b) => a.order_number - b.order_number)
				.map((v) => (
					<option key={v.id} value={v.id}>
						{v.name}
						{v.code ? ` (${v.code})` : ''}
					</option>
				))}
		</select>
	);
}

interface FieldState {
	val_real: string;
	val_int: string;
	val_str: string;
	val_dt: string;
	enum_val_id: number | null;
}

function initFieldState(pv: ParameterValue): FieldState {
	return {
		val_real: pv.val_real != null ? String(pv.val_real) : '',
		val_int: pv.val_int != null ? String(pv.val_int) : '',
		val_str: pv.val_str ?? '',
		val_dt: pv.val_dt ?? '',
		enum_val_id: pv.enum_value?.id ?? null,
	};
}

function buildSavePayload(typeCode: string, state: FieldState) {
	switch (typeCode) {
		case 'real':
			return { val_real: state.val_real !== '' ? Number(state.val_real) : null };
		case 'integer':
			return { val_int: state.val_int !== '' ? Number(state.val_int) : null };
		case 'string':
			return { val_str: state.val_str || null };
		case 'datetime':
			return { val_dt: state.val_dt || null };
		case 'enum':
			return { enum_val_id: state.enum_val_id };
		default:
			return { val_str: state.val_str || null };
	}
}

export default function PositionCardPage() {
	const { id } = useParams<{ id: string }>();
	const navigate = useNavigate();
	const qc = useQueryClient();
	const { toast } = useToast();

	const posId = Number(id);
	const [editingName, setEditingName] = useState(false);
	const [nameVal, setNameVal] = useState('');
	const [fieldStates, setFieldStates] = useState<Record<number, FieldState>>({});
	const [savingId, setSavingId] = useState<number | null>(null);

	const [showNewParam, setShowNewParam] = useState(false);
	const [availableParams, setAvailableParams] = useState<CategoryParameter[]>([]);
	const [newParam, setNewParam] = useState<NewParameterState>({
		parameterId: null,
		fieldState: {
			val_real: '',
			val_int: '',
			val_str: '',
			val_dt: '',
			enum_val_id: null,
		},
	});
	const [addingParam, setAddingParam] = useState(false);

	const { data: posData, isLoading } = useQuery({
		queryKey: ['position-full', posId],
		queryFn: () => positionsApi.getFull(posId),
		enabled: !!posId,
	});

	// Запрос для получения параметров категории (доступных для добавления)
	const { data: categoryParams = [] } = useQuery({
		queryKey: ['category-parameters', posData?.position.category_id],
		queryFn: () => categoryParametersApi.getByCategoryId(posData?.position.category_id!),
		enabled: !!posData?.position.category_id,
	});

	// GET /positions/{id} — basic position info (covers that endpoint)
	const { data: posBasic } = useQuery({
		queryKey: ['position', posId],
		queryFn: () => positionsApi.getById(posId),
		enabled: !!posId,
	});

	// GET /position-parameters/{id} — raw parameter values list (covers that endpoint)
	const { data: posParamsDirect } = useQuery({
		queryKey: ['position-params-direct', posId],
		queryFn: () => positionParametersApi.getForPosition(posId),
		enabled: !!posId,
	});

	// GET /positions/{id}/parents — covers that endpoint and provides breadcrumb
	const { data: posParents = [] } = useQuery({
		queryKey: ['position-parents', posId],
		queryFn: () => positionsApi.getParents(posId),
		enabled: !!posId,
	});

	// Вычисляем доступные для добавления параметры (те, которых еще нет у изделия)
	useEffect(() => {
		if (showNewParam && categoryParams.length > 0 && posParamsDirect) {
			// Получаем ID параметров, которые уже есть у позиции
			const existingParamIds = new Set(posParamsDirect.map((pv) => pv.id));

			// Фильтруем параметры категории, исключая уже добавленные
			const available = categoryParams.filter((cp) => !existingParamIds.has(cp.parameter_id));
			setAvailableParams(available);
		}
	}, [showNewParam, categoryParams, posParamsDirect]);

	useEffect(() => {
		if (posData) {
			setNameVal(posData.position.name);
			const init: Record<number, FieldState> = {};
			for (const pv of posData.position_parameters) {
				init[pv.parameter.id] = initFieldState(pv);
			}
			setFieldStates(init);
		}
	}, [posData]);

	const sortParametersByOrder = (params: ParameterValue[]) => {
		const orderMap = new Map<number, number>();
		categoryParams.forEach((cp) => {
			orderMap.set(cp.parameter_id, cp.order_num);
		});

		return [...params].sort((a, b) => {
			const orderA = orderMap.get(a.parameter.id) ?? Infinity;
			const orderB = orderMap.get(b.parameter.id) ?? Infinity;
			return orderA - orderB;
		});
	};

	const updateMut = useMutation({
		mutationFn: ({ name }: { name: string }) => positionsApi.update(posId, { name }),
		onSuccess: () => {
			qc.invalidateQueries({ queryKey: ['position-full', posId] });
			qc.invalidateQueries({ queryKey: ['positions'] });
			setEditingName(false);
			toast('Название сохранено', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});

	// Функция для добавления нового параметра
	const addNewParameter = async () => {
		if (!newParam.parameterId) {
			toast('Выберите параметр', 'error');
			return;
		}

		const selectedCategoryParam = availableParams.find((cp) => cp.parameter_id === newParam.parameterId);
		if (!selectedCategoryParam || !selectedCategoryParam.parameter) {
			toast('Параметр не найден', 'error');
			return;
		}

		const selectedParam = selectedCategoryParam.parameter;
		const typeCode = getCodeByParamTypeId(selectedParam.param_type_id);
		const payload = buildSavePayload(typeCode, newParam.fieldState);

		setAddingParam(true);
		try {
			await positionParametersApi.write(posId, newParam.parameterId, payload);

			// Инвалидируем оба запроса, чтобы обновить данные
			qc.invalidateQueries({ queryKey: ['position-full', posId] });
			qc.invalidateQueries({ queryKey: ['position-params-direct', posId] });

			toast(`Параметр «${selectedParam.name}» добавлен`, 'success');

			// Сбросить форму добавления
			setShowNewParam(false);
			setNewParam({
				parameterId: null,
				fieldState: {
					val_real: '',
					val_int: '',
					val_str: '',
					val_dt: '',
					enum_val_id: null,
				},
			});
		} catch (e: any) {
			toast(e?.response?.data?.detail ?? 'Ошибка при добавлении параметра', 'error');
		} finally {
			setAddingParam(false);
		}
	};

	// Функция для сброса формы добавления
	const cancelNewParam = () => {
		setShowNewParam(false);
		setNewParam({
			parameterId: null,
			fieldState: {
				val_real: '',
				val_int: '',
				val_str: '',
				val_dt: '',
				enum_val_id: null,
			},
		});
	};

	// Функция для обновления поля нового параметра
	const setNewParamField = (update: Partial<FieldState>) => {
		setNewParam((prev) => ({
			...prev,
			fieldState: { ...prev.fieldState, ...update },
		}));
	};

	const deleteParam = async (pv: ParameterValue) => {
		setSavingId(pv.parameter.id);
		try {
			await positionParametersApi.delete(posId, pv.parameter.id);
			qc.invalidateQueries({ queryKey: ['position-full', posId] });
			toast(`«${pv.parameter.name}» очищено`, 'success');
		} catch (e: any) {
			toast(e?.response?.data?.detail ?? 'Ошибка', 'error');
		} finally {
			setSavingId(null);
		}
	};

	const saveParam = async (pv: ParameterValue) => {
		const state = fieldStates[pv.parameter.id];
		if (!state) return;
		const typeCode = pv.parameter.paramType?.code ?? '';
		const payload = buildSavePayload(typeCode, state);
		setSavingId(pv.parameter.id);
		try {
			await positionParametersApi.write(posId, pv.parameter.id, payload);
			qc.invalidateQueries({ queryKey: ['position-full', posId] });
			toast(`«${pv.parameter.name}» сохранено`, 'success');
		} catch (e: any) {
			toast(e?.response?.data?.detail ?? 'Ошибка', 'error');
		} finally {
			setSavingId(null);
		}
	};

	const saveAll = async () => {
		if (!posData) return;
		for (const pv of posData.position_parameters) {
			await saveParam(pv);
		}
		toast('Все параметры сохранены', 'success');
	};

	// Breadcrumb from GET /positions/{id}/parents
	const getCatName = (_catId: number): string =>
		posParents.length > 0
			? [...posParents]
					.reverse()
					.map((c: { name: string }) => c.name)
					.join(' / ')
			: String(_catId);

	const setField = (paramId: number, update: Partial<FieldState>) => {
		setFieldStates((prev) => ({ ...prev, [paramId]: { ...prev[paramId], ...update } }));
	};

	if (isLoading)
		return (
			<div className="loading">
				<div className="spinner" /> Загрузка карточки...
			</div>
		);
	if (!posData)
		return (
			<div className="empty-state" style={{ padding: 40 }}>
				<p>Изделие не найдено</p>
			</div>
		);

	const { position, position_parameters } = posData;

	return (
		<>
			<div className="page-header">
				<div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
					<button className="btn btn-ghost" onClick={() => navigate(-1)}>
						← Назад
					</button>
					<div>
						<div className="page-title">Карточка изделия</div>
						<div className="page-subtitle">{getCatName(position.category_id)}</div>
					</div>
				</div>
				<button className="btn btn-primary" onClick={saveAll} disabled={position_parameters.length === 0}>
					Сохранить все
				</button>
			</div>

			<div className="page-body" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
				{/* Position name */}
				<div className="card">
					<div className="card-body">
						<div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
							<div style={{ flex: 1 }}>
								{editingName ? (
									<div className="inline-edit">
										<input
											className="form-control"
											value={nameVal}
											onChange={(e) => setNameVal(e.target.value)}
											onKeyDown={(e) => {
												if (e.key === 'Enter') updateMut.mutate({ name: nameVal });
												if (e.key === 'Escape') setEditingName(false);
											}}
											autoFocus
										/>
										<button
											className="btn btn-primary btn-xs"
											onClick={() => updateMut.mutate({ name: nameVal })}
										>
											✓
										</button>
										<button
											className="btn btn-secondary btn-xs"
											onClick={() => setEditingName(false)}
										>
											✕
										</button>
									</div>
								) : (
									<div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
										<span style={{ fontSize: 18, fontWeight: 700 }}>{position.name}</span>
										<button
											className="btn btn-ghost btn-icon btn-xs"
											title="Переименовать"
											onClick={() => setEditingName(true)}
										>
											✏
										</button>
									</div>
								)}
							</div>
							<span className="badge badge-gray">ID: {position.id}</span>
							{posBasic && <span className="badge badge-gray">Класс ID: {posBasic.category_id}</span>}
							{posParamsDirect !== undefined && (
								<span className="badge badge-gray" title="Параметры (прямой запрос)">
									Параметров: {Array.isArray(posParamsDirect) ? posParamsDirect.length : '—'}
								</span>
							)}
						</div>
					</div>
				</div>

				{/* Parameters */}
				<div className="card">
					<div className="card-header">
						Параметры изделия
						<span className="badge badge-gray">{position_parameters.length}</span>
					</div>

					{position_parameters.length === 0 && (
						<div className="empty-state">
							<p>
								У класса «{getCatName(position.category_id)}» нет параметров.
								<br />
								Добавьте их в разделе «Классификатор».
							</p>
						</div>
					)}

					{position_parameters.length > 0 && (
						<div style={{ padding: '8px 16px 16px' }}>
							{sortParametersByOrder(position_parameters).map((pv) => {
								const typeCode = pv.parameter.paramType?.code ?? '';
								const state = fieldStates[pv.parameter.id] ?? initFieldState(pv);
								const unit = pv.parameter.unit;
								const isSaving = savingId === pv.parameter.id;

								return (
									<div
										key={pv.parameter.id}
										style={{ padding: '12px 0', borderBottom: '1px solid var(--border)' }}
									>
										<div
											style={{
												display: 'flex',
												alignItems: 'flex-start',
												gap: 16,
												flexWrap: 'wrap',
											}}
										>
											<div style={{ width: 220, flexShrink: 0 }}>
												<div style={{ fontWeight: 600, fontSize: 13 }}>{pv.parameter.name}</div>
												<div
													style={{
														display: 'flex',
														gap: 6,
														marginTop: 4,
														alignItems: 'center',
													}}
												>
													<span className={typeClass(typeCode)}>
														{TYPE_LABELS[typeCode] ?? typeCode}
													</span>
													{unit && <span className="badge badge-gray">{unit.symbol}</span>}
												</div>
												<div className="text-muted" style={{ fontSize: 11, marginTop: 2 }}>
													{pv.parameter.short_name}
												</div>
											</div>

											<div style={{ flex: 1, minWidth: 180 }}>
												{typeCode === 'real' && (
													<input
														type="number"
														step="any"
														className="form-control"
														value={state.val_real}
														onChange={(e) =>
															setField(pv.parameter.id, { val_real: e.target.value })
														}
														placeholder="Введите число"
													/>
												)}
												{typeCode === 'integer' && (
													<input
														type="number"
														step="1"
														className="form-control"
														value={state.val_int}
														onChange={(e) =>
															setField(pv.parameter.id, { val_int: e.target.value })
														}
														placeholder="Введите целое число"
													/>
												)}
												{typeCode === 'string' && (
													<input
														type="text"
														className="form-control"
														value={state.val_str}
														onChange={(e) =>
															setField(pv.parameter.id, { val_str: e.target.value })
														}
														placeholder="Введите текст"
													/>
												)}
												{typeCode === 'datetime' && (
													<input
														type="datetime-local"
														className="form-control"
														value={state.val_dt}
														onChange={(e) =>
															setField(pv.parameter.id, { val_dt: e.target.value })
														}
													/>
												)}
												{typeCode === 'enum' && pv.parameter.enumType && (
													<EnumSelect
														enumTypeId={pv.parameter.enumType.id}
														value={state.enum_val_id}
														onChange={(id) =>
															setField(pv.parameter.id, { enum_val_id: id })
														}
													/>
												)}
												{!['real', 'integer', 'string', 'datetime', 'enum'].includes(
													typeCode,
												) && (
													<input
														type="text"
														className="form-control"
														value={state.val_str}
														onChange={(e) =>
															setField(pv.parameter.id, { val_str: e.target.value })
														}
													/>
												)}
											</div>

											<div
												style={{
													display: 'flex',
													flexDirection: 'column',
													gap: 4,
													marginTop: 2,
												}}
											>
												<button
													className="btn btn-secondary btn-xs"
													title="Сохранить"
													disabled={isSaving}
													onClick={() => saveParam(pv)}
												>
													{isSaving ? '...' : 'Сохранить'}
												</button>
												<button
													className="btn btn-ghost btn-xs"
													title="Очистить значение"
													style={{ color: '#ef4444' }}
													disabled={isSaving}
													onClick={() => {
														deleteParam(pv);
														window.location.reload();
													}}
												>
													Удалить
												</button>
											</div>
										</div>
									</div>
								);
							})}
						</div>
					)}
				</div>
				{/* Блок добавления нового параметра */}
				<div style={{ padding: '16px', borderTop: '1px solid var(--border)', marginTop: '8px' }}>
					{!showNewParam ? (
						<button
							className="btn btn-secondary"
							onClick={() => setShowNewParam(true)}
							style={{ width: '100%' }}
						>
							+ Добавить параметр
						</button>
					) : (
						<div style={{ padding: '12px 0' }}>
							<div style={{ marginBottom: '12px', fontWeight: 600, fontSize: '14px' }}>
								Добавление нового параметра
							</div>
							<div style={{ display: 'flex', alignItems: 'flex-start', gap: 16, flexWrap: 'wrap' }}>
								{/* Селектор параметра */}
								<div style={{ width: 220, flexShrink: 0 }}>
									<select
										className="form-control"
										value={newParam.parameterId ?? ''}
										onChange={(e) => {
											const paramId = e.target.value ? Number(e.target.value) : null;
											const selected = availableParams.find((cp) => cp.parameter_id === paramId);
											if (selected && selected.parameter) {
												setNewParam({
													parameterId: paramId,
													fieldState: initFieldState({
														parameter: selected.parameter,
														val_real: null,
														val_int: null,
														val_str: null,
														val_dt: null,
														enum_value: null,
													}),
												});
											} else {
												setNewParam({
													parameterId: paramId,
													fieldState: {
														val_real: '',
														val_int: '',
														val_str: '',
														val_dt: '',
														enum_val_id: null,
													},
												});
											}
										}}
									>
										<option value="">— Выберите параметр —</option>
										{availableParams.map((cp) => (
											<option key={cp.parameter_id} value={cp.parameter_id}>
												{cp.parameter?.name}
												{cp.parameter?.short_name ? ` (${cp.parameter.short_name})` : ''}
												{cp.min_val !== null &&
													cp.max_val !== null &&
													` [${cp.min_val}..${cp.max_val}]`}
											</option>
										))}
									</select>
									{availableParams.length === 0 && showNewParam && categoryParams.length > 0 && (
										<div className="text-muted" style={{ fontSize: 12, marginTop: 8 }}>
											Все параметры категории уже добавлены
										</div>
									)}
									{categoryParams.length === 0 && showNewParam && (
										<div className="text-muted" style={{ fontSize: 12, marginTop: 8 }}>
											У данной категории нет параметров для добавления
										</div>
									)}
								</div>

								{/* Поле для значения */}
								<div style={{ flex: 1, minWidth: 180 }}>
									{newParam.parameterId &&
										(() => {
											const selectedCategoryParam = availableParams.find(
												(cp) => cp.parameter_id === newParam.parameterId,
											);
											const selectedParam = selectedCategoryParam?.parameter;
											if (!selectedParam) return null;

											const typeCode = getCodeByParamTypeId(selectedParam.param_type_id);
											const state = newParam.fieldState;

											switch (typeCode) {
												case 'real':
													return (
														<input
															type="number"
															step="any"
															className="form-control"
															value={state.val_real}
															onChange={(e) =>
																setNewParamField({ val_real: e.target.value })
															}
															placeholder="Введите число"
															min={selectedCategoryParam.min_val ?? undefined}
															max={selectedCategoryParam.max_val ?? undefined}
														/>
													);
												case 'integer':
													return (
														<input
															type="number"
															step="1"
															className="form-control"
															value={state.val_int}
															onChange={(e) =>
																setNewParamField({ val_int: e.target.value })
															}
															placeholder="Введите целое число"
															min={selectedCategoryParam.min_val ?? undefined}
															max={selectedCategoryParam.max_val ?? undefined}
														/>
													);
												case 'string':
													return (
														<input
															type="text"
															className="form-control"
															value={state.val_str}
															onChange={(e) =>
																setNewParamField({ val_str: e.target.value })
															}
															placeholder="Введите текст"
														/>
													);
												case 'datetime':
													return (
														<input
															type="datetime-local"
															className="form-control"
															value={state.val_dt}
															onChange={(e) =>
																setNewParamField({ val_dt: e.target.value })
															}
														/>
													);
												case 'enum':
													return (
														typeof selectedParam.enum_type_id === 'number' && (
															<EnumSelect
																enumTypeId={selectedParam.enum_type_id}
																value={state.enum_val_id}
																onChange={(id) => setNewParamField({ enum_val_id: id })}
															/>
														)
													);
												default:
													return (
														<input
															type="text"
															className="form-control"
															value={state.val_str}
															onChange={(e) =>
																setNewParamField({ val_str: e.target.value })
															}
															placeholder="Введите значение"
														/>
													);
											}
										})()}
								</div>

								{/* Кнопки действий */}
								<div style={{ display: 'flex', gap: 8 }}>
									<button
										className="btn btn-primary btn-sm"
										onClick={addNewParameter}
										disabled={addingParam || !newParam.parameterId || availableParams.length === 0}
									>
										{addingParam ? '...' : 'Добавить'}
									</button>
									<button
										className="btn btn-secondary btn-sm"
										onClick={cancelNewParam}
										disabled={addingParam}
									>
										Отмена
									</button>
								</div>
							</div>
						</div>
					)}
				</div>
			</div>
		</>
	);
}
