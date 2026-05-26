import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { parametersApi } from '../api/parameters';
import { enumsApi } from '../api/enums';
import { unitsApi } from '../api/units';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';
import { PARAM_TYPE_CODES } from '../types';
import type { Parameter } from '../types';

export default function ParametersPage() {
	const qc = useQueryClient();
	const { toast } = useToast();

	const [addModal, setAddModal] = useState(false);
	const [deleteModal, setDeleteModal] = useState<Parameter | null>(null);
	const [detailModal, setDetailModal] = useState<Parameter | null>(null);
	const [form, setForm] = useState({
		short_name: '',
		name: '',
		param_type_code: 'real',
		enum_type_id: '',
		unit_id: '',
	});

	const { data: params = [], isLoading } = useQuery({ queryKey: ['parameters'], queryFn: parametersApi.getAll });
	const { data: enumTypes = [] } = useQuery({ queryKey: ['enum-types'], queryFn: enumsApi.getTypes });
	const { data: units = [] } = useQuery({ queryKey: ['units'], queryFn: unitsApi.getAll });
	// All enum values — used to resolve param_type_id → code string
	const { data: allEnumValues = [] } = useQuery({ queryKey: ['enum-values-all'], queryFn: enumsApi.getValues });
	// GET /parameters/{id} — fetch fresh detail when viewing
	const { data: paramDetail } = useQuery({
		queryKey: ['parameter', detailModal?.id],
		queryFn: () => parametersApi.getById(detailModal!.id),
		enabled: !!detailModal,
	});

	// Роль: 'user' или 'admin'
	const [role] = useState<'user' | 'admin'>(() => {
		return (localStorage.getItem('app_role') as 'user' | 'admin') || 'user';
	});

	// Map: enum_value.id → {code, name} for resolving param_type_id
	const typeEnumMap = new Map(allEnumValues.map((v) => [v.id, v]));

	const invalidate = () => qc.invalidateQueries({ queryKey: ['parameters'] });

	const createMut = useMutation({
		mutationFn: () =>
			parametersApi.create({
				short_name: form.short_name.trim(),
				name: form.name.trim(),
				param_type_code: form.param_type_code,
				enum_type_id: form.enum_type_id ? Number(form.enum_type_id) : null,
				unit_id: form.unit_id ? Number(form.unit_id) : null,
			}),
		onSuccess: () => {
			invalidate();
			setAddModal(false);
			setForm({ short_name: '', name: '', param_type_code: 'real', enum_type_id: '', unit_id: '' });
			toast('Параметр создан', 'success');
		},
		onError: (e: any) => toast(e?.response?.data?.detail ?? 'Ошибка', 'error'),
	});

	const deleteMut = useMutation({
		mutationFn: (id: number) => parametersApi.delete(id),
		onSuccess: () => {
			invalidate();
			setDeleteModal(null);
			toast('Удалено', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});

	const isEnum = form.param_type_code === 'enum';

	return (
		<>
			<div className="page-header">
				<div>
					<div className="page-title">Параметры</div>
				</div>
				<button
					className="btn btn-primary"
					onClick={() => {
						if (role !== 'admin') {
							return alert('Нет доступа');
						}

						setAddModal(true);
					}}
				>
					+ Новый параметр
				</button>
			</div>

			<div className="page-body">
				<div className="card">
					<div className="card-header">
						Все параметры
						<span className="badge badge-gray">{params.length}</span>
					</div>
					{isLoading && (
						<div className="loading">
							<div className="spinner" /> Загрузка...
						</div>
					)}
					{!isLoading && params.length === 0 && (
						<div className="empty-state">
							<p>Нет параметров</p>
						</div>
					)}
					{params.length > 0 && (
						<div className="table-wrap">
							<table>
								<thead>
									<tr>
										<th>ID</th>
										<th>Краткое имя</th>
										<th>Название</th>
										<th>Тип</th>
										<th>Enum тип</th>
										<th>Ед.изм.</th>
										<th></th>
									</tr>
								</thead>
								<tbody>
									{params.map((p) => {
										const et = enumTypes.find((e) => e.id === p.enum_type_id);
										const u = units.find((u) => u.id === p.unit_id);
										const typeEV = typeEnumMap.get(p.param_type_id);
										const typeCode = typeEV?.code ?? null;
										return (
											<tr key={p.id}>
												<td className="text-muted font-mono">{p.id}</td>
												<td>
													<span className="font-mono" style={{ fontWeight: 600 }}>
														{p.short_name}
													</span>
												</td>
												<td>{p.name}</td>
												<td>
													{typeCode ? (
														<span className={`badge type-${typeCode}`}>{typeCode}</span>
													) : (
														<span className="badge badge-gray font-mono">
															{p.param_type_id}
														</span>
													)}
												</td>
												<td>
													{et ? (
														<span className="badge badge-purple">{et.code}</span>
													) : (
														<span className="text-muted">—</span>
													)}
												</td>
												<td>
													{u ? (
														<span className="badge badge-gray">{u.symbol}</span>
													) : (
														<span className="text-muted">—</span>
													)}
												</td>
												<td>
													<div className="td-actions">
														<button
															className="btn btn-ghost btn-icon btn-xs"
															title="Подробнее"
															onClick={() => setDetailModal(p)}
														>
															i
														</button>
														<button
															className="btn btn-ghost btn-icon btn-xs"
															style={{ color: '#ef4444' }}
															title="Удалить"
															onClick={() => {
																if (role !== 'admin') {
																	return alert('Нет доступа');
																}

																setDeleteModal(p);
															}}
														>
															✕
														</button>
													</div>
												</td>
											</tr>
										);
									})}
								</tbody>
							</table>
						</div>
					)}
				</div>
			</div>

			{/* Add modal */}
			<Modal
				open={addModal}
				onClose={() => setAddModal(false)}
				title="Новый параметр"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setAddModal(false)}>
							Отмена
						</button>
						<button
							className="btn btn-primary"
							disabled={
								!form.short_name.trim() ||
								!form.name.trim() ||
								createMut.isPending ||
								(isEnum && !form.enum_type_id)
							}
							onClick={() => createMut.mutate()}
						>
							Создать
						</button>
					</>
				}
			>
				<div className="form-row">
					<div className="form-group" style={{ flex: '0 0 140px' }}>
						<label className="form-label">Краткое имя</label>
						<input
							className="form-control font-mono"
							value={form.short_name}
							onChange={(e) => setForm((f) => ({ ...f, short_name: e.target.value }))}
							placeholder="calories"
							autoFocus
						/>
					</div>
					<div className="form-group">
						<label className="form-label">Полное название</label>
						<input
							className="form-control"
							value={form.name}
							onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
							placeholder="Калорийность"
						/>
					</div>
				</div>
				<div className="form-group">
					<label className="form-label">Тип параметра</label>
					<select
						className="form-control"
						value={form.param_type_code}
						onChange={(e) => setForm((f) => ({ ...f, param_type_code: e.target.value, enum_type_id: '' }))}
					>
						{PARAM_TYPE_CODES.map((t) => (
							<option key={t.code} value={t.code}>
								{t.label} ({t.code})
							</option>
						))}
					</select>
				</div>
				{isEnum && (
					<div className="form-group">
						<label className="form-label">Тип перечисления</label>
						<select
							className="form-control"
							value={form.enum_type_id}
							onChange={(e) => setForm((f) => ({ ...f, enum_type_id: e.target.value }))}
						>
							<option value="">— Выберите —</option>
							{enumTypes.map((et) => (
								<option key={et.id} value={et.id}>
									{et.name} ({et.code})
								</option>
							))}
						</select>
						{enumTypes.length === 0 && (
							<span className="form-hint text-danger">
								Нет перечислений. Создайте в разделе «Перечисления».
							</span>
						)}
					</div>
				)}
				{(form.param_type_code === 'real' || form.param_type_code === 'integer') && (
					<div className="form-group">
						<label className="form-label">Единица измерения</label>
						<select
							className="form-control"
							value={form.unit_id}
							onChange={(e) => setForm((f) => ({ ...f, unit_id: e.target.value }))}
						>
							<option value="">— Нет —</option>
							{units.map((u) => (
								<option key={u.id} value={u.id}>
									{u.name} ({u.symbol})
								</option>
							))}
						</select>
					</div>
				)}
			</Modal>

			{/* Detail modal (GET /parameters/{id}) */}
			<Modal
				open={detailModal !== null}
				onClose={() => setDetailModal(null)}
				title={`Параметр${paramDetail ? ` #${paramDetail.id}` : ''}`}
				footer={
					<button className="btn btn-secondary" onClick={() => setDetailModal(null)}>
						Закрыть
					</button>
				}
			>
				{paramDetail ? (
					(() => {
						const typeEV = typeEnumMap.get(paramDetail.param_type_id);
						const typeCode = typeEV?.code ?? null;
						const et = enumTypes.find((e) => e.id === paramDetail.enum_type_id);
						const u = units.find((u) => u.id === paramDetail.unit_id);
						return (
							<div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
								<div style={{ display: 'flex', gap: 8, alignItems: 'baseline' }}>
									<span className="text-muted" style={{ minWidth: 120 }}>
										Краткое имя
									</span>
									<span className="font-mono" style={{ fontWeight: 600 }}>
										{paramDetail.short_name}
									</span>
								</div>
								<div style={{ display: 'flex', gap: 8, alignItems: 'baseline' }}>
									<span className="text-muted" style={{ minWidth: 120 }}>
										Полное название
									</span>
									<span>{paramDetail.name}</span>
								</div>
								<div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
									<span className="text-muted" style={{ minWidth: 120 }}>
										Тип данных
									</span>
									<span style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
										{typeCode ? (
											<span className={`badge type-${typeCode}`}>{typeCode}</span>
										) : (
											<span className="badge badge-gray">{paramDetail.param_type_id}</span>
										)}
										{typeEV?.name && (
											<span className="text-muted" style={{ fontSize: 12 }}>
												{typeEV.name}
											</span>
										)}
									</span>
								</div>
								{et && (
									<div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
										<span className="text-muted" style={{ minWidth: 120 }}>
											Перечисление
										</span>
										<span className="badge badge-purple">{et.code}</span>
										<span className="text-muted" style={{ fontSize: 12 }}>
											{et.name}
										</span>
									</div>
								)}
								{u && (
									<div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
										<span className="text-muted" style={{ minWidth: 120 }}>
											Единица измерения
										</span>
										<span className="badge badge-gray">{u.symbol}</span>
										<span className="text-muted" style={{ fontSize: 12 }}>
											{u.name}
										</span>
									</div>
								)}
							</div>
						);
					})()
				) : (
					<div className="loading">
						<div className="spinner" /> Загрузка...
					</div>
				)}
			</Modal>

			{/* Delete modal */}
			<Modal
				open={deleteModal !== null}
				onClose={() => setDeleteModal(null)}
				title="Удалить параметр"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setDeleteModal(null)}>
							Отмена
						</button>
						<button
							className="btn btn-danger"
							disabled={deleteMut.isPending}
							onClick={() => deleteModal && deleteMut.mutate(deleteModal.id)}
						>
							Удалить
						</button>
					</>
				}
			>
				<p>
					Удалить параметр <strong>«{deleteModal?.name}»</strong>?
				</p>
				<p className="text-muted" style={{ marginTop: 6, fontSize: 12 }}>
					Параметр будет удалён из всех классов, где он используется.
				</p>
			</Modal>
		</>
	);
}
