import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { enumsApi } from '../api/enums';
import { unitsApi } from '../api/units';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';
import type { EnumType, EnumValue } from '../types';

export default function EnumEditorPage() {
	const qc = useQueryClient();
	const { toast } = useToast();
	const [selectedTypeId, setSelectedTypeId] = useState<number | null>(null);

	// Validate
	const [validateInput, setValidateInput] = useState('');
	const [validateResult, setValidateResult] = useState<{ valid: boolean; id: number; name: string } | null>(null);
	const [validating, setValidating] = useState(false);

	// Modals
	const [typeModal, setTypeModal] = useState<{ open: boolean; editing: EnumType | null }>({
		open: false,
		editing: null,
	});
	const [deleteTypeModal, setDeleteTypeModal] = useState<EnumType | null>(null);
	const [valueModal, setValueModal] = useState<{ open: boolean; editing: EnumValue | null }>({
		open: false,
		editing: null,
	});
	const [deleteValueModal, setDeleteValueModal] = useState<EnumValue | null>(null);

	// Form state
	const [typeForm, setTypeForm] = useState({ name: '', code: '' });
	const [valueForm, setValueForm] = useState({
		order_number: '1',
		name: '',
		code: '',
		numeric_value: '',
		unit_id: '',
	});

	// Роль: 'user' или 'admin'
	const [role] = useState<'user' | 'admin'>(() => {
		return (localStorage.getItem('app_role') as 'user' | 'admin') || 'user';
	});

	const { data: types = [], isLoading: typesLoading } = useQuery({
		queryKey: ['enum-types'],
		queryFn: enumsApi.getTypes,
	});
	// GET /enum/types/{id} — fetch fresh type detail when one is selected
	const { data: selectedTypeDetail } = useQuery({
		queryKey: ['enum-type-detail', selectedTypeId],
		queryFn: () => enumsApi.getType(selectedTypeId!),
		enabled: selectedTypeId !== null,
	});
	const { data: values = [], isLoading: valuesLoading } = useQuery({
		queryKey: ['enum-values', selectedTypeId],
		queryFn: () => enumsApi.getTypeValues(selectedTypeId!),
		enabled: selectedTypeId !== null,
	});
	// GET /enum/values/{id} — fetch fresh value detail when editing
	const { data: editingValueDetail } = useQuery({
		queryKey: ['enum-value-detail', valueModal.editing?.id],
		queryFn: () => enumsApi.getValue(valueModal.editing!.id),
		enabled: !!valueModal.editing,
	});
	const { data: units = [] } = useQuery({ queryKey: ['units'], queryFn: unitsApi.getAll });

	const selectedType = types.find((t) => t.id === selectedTypeId);

	const invalidateTypes = () => qc.invalidateQueries({ queryKey: ['enum-types'] });
	const invalidateValues = () => qc.invalidateQueries({ queryKey: ['enum-values', selectedTypeId] });

	const openAddType = () => {
		setTypeForm({ name: '', code: '' });
		setTypeModal({ open: true, editing: null });
	};
	const openEditType = (t: EnumType) => {
		setTypeForm({ name: t.name, code: t.code });
		setTypeModal({ open: true, editing: t });
	};
	const openAddValue = () => {
		setValueForm({
			order_number: String((values.length || 0) + 1),
			name: '',
			code: '',
			numeric_value: '',
			unit_id: '',
		});
		setValueModal({ open: true, editing: null });
	};
	const openEditValue = (v: EnumValue) => {
		setValueForm({
			order_number: String(v.order_number),
			name: v.name,
			code: v.code ?? '',
			numeric_value: v.numeric_value != null ? String(v.numeric_value) : '',
			unit_id: v.unit_id != null ? String(v.unit_id) : '',
		});
		setValueModal({ open: true, editing: v });
	};

	const createTypeMut = useMutation({
		mutationFn: (d: { name: string; code: string }) => enumsApi.createType(d),
		onSuccess: () => {
			invalidateTypes();
			setTypeModal({ open: false, editing: null });
			toast('Тип создан', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});
	const updateTypeMut = useMutation({
		mutationFn: ({ id, d }: { id: number; d: Partial<{ name: string; code: string }> }) =>
			enumsApi.updateType(id, d),
		onSuccess: () => {
			invalidateTypes();
			setTypeModal({ open: false, editing: null });
			toast('Тип обновлён', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});
	const deleteTypeMut = useMutation({
		mutationFn: (id: number) => enumsApi.deleteType(id),
		onSuccess: () => {
			invalidateTypes();
			if (deleteTypeModal?.id === selectedTypeId) setSelectedTypeId(null);
			setDeleteTypeModal(null);
			toast('Удалено', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});

	const createValueMut = useMutation({
		mutationFn: (d: Parameters<typeof enumsApi.createValue>[0]) => enumsApi.createValue(d),
		onSuccess: () => {
			invalidateValues();
			setValueModal({ open: false, editing: null });
			toast('Значение добавлено', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});
	const updateValueMut = useMutation({
		mutationFn: ({ id, d }: { id: number; d: Parameters<typeof enumsApi.updateValue>[1] }) =>
			enumsApi.updateValue(id, d),
		onSuccess: () => {
			invalidateValues();
			setValueModal({ open: false, editing: null });
			toast('Обновлено', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});
	const deleteValueMut = useMutation({
		mutationFn: (id: number) => enumsApi.deleteValue(id),
		onSuccess: () => {
			invalidateValues();
			setDeleteValueModal(null);
			toast('Удалено', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});

	const submitType = () => {
		const d = { name: typeForm.name.trim(), code: typeForm.code.trim() };
		if (!d.name || !d.code) return;
		typeModal.editing ? updateTypeMut.mutate({ id: typeModal.editing.id, d }) : createTypeMut.mutate(d);
	};

	const doValidate = async () => {
		if (!selectedType || !validateInput.trim()) return;
		setValidating(true);
		setValidateResult(null);
		try {
			const res = await enumsApi.validate(selectedType.code, validateInput.trim());
			setValidateResult(res);
		} catch {
			setValidateResult(null);
			toast('Значение не найдено', 'info');
		} finally {
			setValidating(false);
		}
	};

	const submitValue = () => {
		if (!selectedTypeId) return;
		const d = {
			enum_type_id: selectedTypeId,
			order_number: Number(valueForm.order_number),
			name: valueForm.name.trim(),
			code: valueForm.code.trim() || null,
			numeric_value: valueForm.numeric_value !== '' ? Number(valueForm.numeric_value) : null,
			unit_id: valueForm.unit_id !== '' ? Number(valueForm.unit_id) : null,
		};
		if (!d.name) return;
		valueModal.editing ? updateValueMut.mutate({ id: valueModal.editing.id, d }) : createValueMut.mutate(d);
	};

	return (
		<>
			<div className="page-header">
				<div>
					<div className="page-title">Перечисления</div>
				</div>
			</div>

			<div className="page-body">
				<div className="split-panel">
					{/* Types */}
					<div className="split-left card flex-col">
						<div className="card-header">
							Типы перечислений
							<button
								className="btn btn-primary btn-xs"
								onClick={() => {
									if (role !== 'admin') {
										return alert('Нет доступа');
									}

									openAddType();
								}}
							>
								+ Добавить
							</button>
						</div>
						<div style={{ flex: 1, overflowY: 'auto' }}>
							{typesLoading && (
								<div className="loading">
									<div className="spinner" /> Загрузка...
								</div>
							)}
							{!typesLoading && types.length === 0 && (
								<div className="empty-state">
									<p>Нет типов</p>
								</div>
							)}
							{types.map((t) => (
								<div
									key={t.id}
									className={`tree-node-row${selectedTypeId === t.id ? ' selected' : ''}`}
									style={{ padding: '10px 12px' }}
									onClick={() => setSelectedTypeId(t.id)}
								>
									<div style={{ flex: 1 }}>
										<div style={{ fontWeight: 500, fontSize: 13 }}>{t.name}</div>
										<div className="font-mono text-muted">{t.code}</div>
									</div>
									<div className="tree-actions">
										<button
											className="btn btn-ghost btn-icon btn-xs"
											onClick={(e) => {
												if (role !== 'admin') {
													return alert('Нет доступа');
												}

												e.stopPropagation();
												openEditType(t);
											}}
										>
											✏
										</button>
										<button
											className="btn btn-ghost btn-icon btn-xs"
											style={{ color: '#ef4444' }}
											onClick={(e) => {
												if (role !== 'admin') {
													return alert('Нет доступа');
												}

												e.stopPropagation();
												setDeleteTypeModal(t);
											}}
										>
											✕
										</button>
									</div>
								</div>
							))}
						</div>
					</div>

					{/* Values */}
					<div className="split-right card flex-col">
						{selectedType ? (
							<>
								<div className="card-header">
									<span>
										Значения: <strong>{selectedTypeDetail?.name ?? selectedType.name}</strong>
										<span className="font-mono text-muted">
											{' '}
											({selectedTypeDetail?.code ?? selectedType.code})
										</span>
										<span className="badge badge-gray" style={{ marginLeft: 6, fontSize: 10 }}>
											ID {selectedType.id}
										</span>
									</span>
									<button
										className="btn btn-primary btn-xs"
										onClick={() => {
											if (role !== 'admin') {
												return alert('Нет доступа');
											}

											openAddValue();
										}}
									>
										+ Добавить значение
									</button>
								</div>
								<div style={{ flex: 1, overflowY: 'auto', padding: 0 }}>
									{valuesLoading && (
										<div className="loading">
											<div className="spinner" /> Загрузка...
										</div>
									)}
									{!valuesLoading && values.length === 0 && (
										<div className="empty-state">
											<p>Нет значений</p>
										</div>
									)}
									{values.length > 0 && (
										<div className="table-wrap">
											<table>
												<thead>
													<tr>
														<th>#</th>
														<th>Порядок</th>
														<th>Название</th>
														<th>Код</th>
														<th>Числовое</th>
														<th>Ед.изм.</th>
														<th></th>
													</tr>
												</thead>
												<tbody>
													{[...values]
														.sort((a, b) => a.order_number - b.order_number)
														.map((v) => (
															<tr key={v.id}>
																<td className="text-muted font-mono">{v.id}</td>
																<td>{v.order_number}</td>
																<td style={{ fontWeight: 500 }}>{v.name}</td>
																<td>
																	<span className="font-mono">
																		{v.code ?? (
																			<span className="text-muted">—</span>
																		)}
																	</span>
																</td>
																<td>
																	{v.numeric_value ?? (
																		<span className="text-muted">—</span>
																	)}
																</td>
																<td>
																	{v.unit_id ? (
																		(units.find((u) => u.id === v.unit_id)
																			?.symbol ?? v.unit_id)
																	) : (
																		<span className="text-muted">—</span>
																	)}
																</td>
																<td>
																	<div className="td-actions">
																		<button
																			className="btn btn-ghost btn-icon btn-xs"
																			onClick={() => {
																				if (role !== 'admin') {
																					return alert('Нет доступа');
																				}

																				openEditValue(v);
																			}}
																		>
																			✏
																		</button>
																		<button
																			className="btn btn-ghost btn-icon btn-xs"
																			style={{ color: '#ef4444' }}
																			onClick={() => {
																				if (role !== 'admin') {
																					return alert('Нет доступа');
																				}

																				setDeleteValueModal(v);
																			}}
																		>
																			✕
																		</button>
																	</div>
																</td>
															</tr>
														))}
												</tbody>
											</table>
										</div>
									)}
								</div>

								{/* ── Validate panel ── */}
								{/* <div style={{ borderTop: '1px solid var(--border)', padding: '12px 16px', background: '#f8fafc' }}>
                  <div className="form-label" style={{ marginBottom: 8 }}>
                    Проверить значение (POST /enum/validate)
                  </div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                    <input className="form-control" style={{ flex: 1, minWidth: 140 }}
                      placeholder={`код или название значения…`}
                      value={validateInput}
                      onChange={e => { setValidateInput(e.target.value); setValidateResult(null); }}
                      onKeyDown={e => e.key === 'Enter' && doValidate()} />
                    <button className="btn btn-secondary" disabled={!validateInput.trim() || validating} onClick={doValidate}>
                      {validating ? '...' : 'Проверить'}
                    </button>
                  </div>
                  {validateResult !== null && (
                    <div style={{ marginTop: 8, fontSize: 13 }}>
                      {validateResult.valid ? (
                        <span style={{ color: 'var(--success)' }}>
                          Найдено: <strong>{validateResult.name}</strong> (ID {validateResult.id})
                        </span>
                      ) : (
                        <span style={{ color: 'var(--danger)' }}>Значение не найдено в типе «{selectedType?.code}»</span>
                      )}
                    </div>
                  )}
                </div> */}
							</>
						) : (
							<div
								className="empty-state"
								style={{ flex: 1, justifyContent: 'center', display: 'flex', flexDirection: 'column' }}
							>
								<p>
									Выберите тип перечисления
									<br />
									для управления его значениями
								</p>
							</div>
						)}
					</div>
				</div>
			</div>

			{/* Type modal */}
			<Modal
				open={typeModal.open}
				onClose={() => setTypeModal({ open: false, editing: null })}
				title={typeModal.editing ? 'Редактировать тип' : 'Новый тип перечисления'}
				footer={
					<>
						<button
							className="btn btn-secondary"
							onClick={() => setTypeModal({ open: false, editing: null })}
						>
							Отмена
						</button>
						<button
							className="btn btn-primary"
							onClick={submitType}
							disabled={!typeForm.name || !typeForm.code}
						>
							{typeModal.editing ? 'Сохранить' : 'Создать'}
						</button>
					</>
				}
			>
				<div className="form-group">
					<label className="form-label">Название</label>
					<input
						className="form-control"
						value={typeForm.name}
						onChange={(e) => setTypeForm((f) => ({ ...f, name: e.target.value }))}
						autoFocus
					/>
				</div>
				<div className="form-group">
					<label className="form-label">Код</label>
					<input
						className="form-control font-mono"
						value={typeForm.code}
						onChange={(e) => setTypeForm((f) => ({ ...f, code: e.target.value }))}
						placeholder="my_enum_code"
					/>
					<span className="form-hint">Уникальный идентификатор, только латиница и _</span>
				</div>
			</Modal>

			{/* Delete type */}
			<Modal
				open={deleteTypeModal !== null}
				onClose={() => setDeleteTypeModal(null)}
				title="Удалить тип"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setDeleteTypeModal(null)}>
							Отмена
						</button>
						<button
							className="btn btn-danger"
							disabled={deleteTypeMut.isPending}
							onClick={() => deleteTypeModal && deleteTypeMut.mutate(deleteTypeModal.id)}
						>
							Удалить
						</button>
					</>
				}
			>
				<p>
					Удалить тип <strong>«{deleteTypeModal?.name}»</strong> и все его значения?
				</p>
			</Modal>

			{/* Value modal */}
			<Modal
				open={valueModal.open}
				onClose={() => setValueModal({ open: false, editing: null })}
				title={
					valueModal.editing
						? `Редактировать значение${editingValueDetail ? ` — ID ${editingValueDetail.id}` : ''}`
						: 'Новое значение'
				}
				footer={
					<>
						<button
							className="btn btn-secondary"
							onClick={() => setValueModal({ open: false, editing: null })}
						>
							Отмена
						</button>
						<button className="btn btn-primary" onClick={submitValue} disabled={!valueForm.name.trim()}>
							{valueModal.editing ? 'Сохранить' : 'Добавить'}
						</button>
					</>
				}
			>
				<div className="form-row">
					<div className="form-group" style={{ flex: '0 0 100px' }}>
						<label className="form-label">Порядок</label>
						<input
							type="number"
							className="form-control"
							value={valueForm.order_number}
							onChange={(e) => setValueForm((f) => ({ ...f, order_number: e.target.value }))}
						/>
					</div>
					<div className="form-group">
						<label className="form-label">Название</label>
						<input
							className="form-control"
							value={valueForm.name}
							onChange={(e) => setValueForm((f) => ({ ...f, name: e.target.value }))}
							autoFocus
						/>
					</div>
				</div>
				<div className="form-row">
					<div className="form-group">
						<label className="form-label">Код</label>
						<input
							className="form-control font-mono"
							value={valueForm.code}
							placeholder="my_value"
							onChange={(e) => setValueForm((f) => ({ ...f, code: e.target.value }))}
						/>
					</div>
					<div className="form-group">
						<label className="form-label">Числовое значение</label>
						<input
							type="number"
							className="form-control"
							value={valueForm.numeric_value}
							placeholder="—"
							onChange={(e) => setValueForm((f) => ({ ...f, numeric_value: e.target.value }))}
						/>
					</div>
				</div>
				<div className="form-group">
					<label className="form-label">Единица измерения</label>
					<select
						className="form-control"
						value={valueForm.unit_id}
						onChange={(e) => setValueForm((f) => ({ ...f, unit_id: e.target.value }))}
					>
						<option value="">— Нет —</option>
						{units.map((u) => (
							<option key={u.id} value={u.id}>
								{u.name} ({u.symbol})
							</option>
						))}
					</select>
				</div>
			</Modal>

			{/* Delete value */}
			<Modal
				open={deleteValueModal !== null}
				onClose={() => setDeleteValueModal(null)}
				title="Удалить значение"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setDeleteValueModal(null)}>
							Отмена
						</button>
						<button
							className="btn btn-danger"
							disabled={deleteValueMut.isPending}
							onClick={() => deleteValueModal && deleteValueMut.mutate(deleteValueModal.id)}
						>
							Удалить
						</button>
					</>
				}
			>
				<p>
					Удалить значение <strong>«{deleteValueModal?.name}»</strong>?
				</p>
			</Modal>
		</>
	);
}
