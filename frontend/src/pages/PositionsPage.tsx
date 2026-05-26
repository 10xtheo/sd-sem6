import { useState, useId } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { positionsApi } from '../api/positions';
import { categoriesApi } from '../api/categories';
import { categoryParametersApi } from '../api/categoryParameters';
import { enumsApi } from '../api/enums';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';
import type { Category, Position, PositionFull, ParameterValue } from '../types';

// ─── helpers ──────────────────────────────────────────────────────────────────

function buildFlatWithPath(cats: Category[]): { id: number; label: string }[] {
	const map = new Map<number, Category>();
	for (const c of cats) map.set(c.id, c);
	const getPath = (id: number): string => {
		const cat = map.get(id);
		if (!cat) return String(id);
		return cat.parent_id === null ? cat.name : getPath(cat.parent_id) + ' / ' + cat.name;
	};
	return cats.map((c) => ({ id: c.id, label: getPath(c.id) })).sort((a, b) => a.label.localeCompare(b.label));
}

function displayValue(pv: ParameterValue): string {
	if (pv.enum_value) return pv.enum_value.name;
	if (pv.val_real != null) return String(pv.val_real);
	if (pv.val_int != null) return String(pv.val_int);
	if (pv.val_str != null) return pv.val_str;
	if (pv.val_dt != null) return pv.val_dt.replace('T', ' ').slice(0, 16);
	return '—';
}

// ─── filter row types ─────────────────────────────────────────────────────────

type FilterOp = 'eq' | 'min' | 'max' | 'contains';

interface FilterRow {
	uid: string;
	short_name: string;
	op: FilterOp;
	value: string;
}

const OP_LABELS: Record<FilterOp, string> = {
	eq: '= равно',
	min: '≥ мин',
	max: '≤ макс',
	contains: '~ содержит',
};

function buildSearchParams(name: string, categoryId: string, filters: FilterRow[]): Record<string, string | number> {
	const p: Record<string, string | number> = {};
	if (name.trim()) p['name'] = name.trim();
	if (categoryId) p['category_id'] = Number(categoryId);
	for (const f of filters) {
		if (!f.short_name || !f.value.trim()) continue;
		const key =
			f.op === 'eq'
				? f.short_name
				: f.op === 'min'
					? `${f.short_name}_min`
					: f.op === 'max'
						? `${f.short_name}_max`
						: `${f.short_name}_contains`;
		p[key] = f.value.trim();
	}
	return p;
}

// ─── EnumSelect helper ────────────────────────────────────────────────────────

function EnumValueSelect({
	enumTypeId,
	value,
	onChange,
}: {
	enumTypeId: number;
	value: string;
	onChange: (v: string) => void;
}) {
	const { data: vals = [] } = useQuery({
		queryKey: ['enum-values', enumTypeId],
		queryFn: () => enumsApi.getTypeValues(enumTypeId),
	});
	return (
		<select
			className="form-control"
			value={value}
			onChange={(e) => onChange(e.target.value)}
			style={{ flex: 1, minWidth: 100 }}
		>
			<option value="">— любое —</option>
			{[...vals]
				.sort((a, b) => a.order_number - b.order_number)
				.map((v) => (
					<option key={v.id} value={v.code ?? String(v.id)}>
						{v.name}
					</option>
				))}
		</select>
	);
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function PositionsPage() {
	const navigate = useNavigate();
	const qc = useQueryClient();
	const { toast } = useToast();
	const uid = useId();

	// Search state
	const [nameFilter, setNameFilter] = useState('');
	const [categoryId, setCategoryId] = useState('');
	const [filterRows, setFilterRows] = useState<FilterRow[]>([]);
	const [searchParams, setSearchParams] = useState<Record<string, string | number>>({});
	const [hasSearched, setHasSearched] = useState(false);

	// Modals
	const [addModal, setAddModal] = useState(false);
	const [moveModal, setMoveModal] = useState<Position | null>(null);
	const [deleteModal, setDeleteModal] = useState<PositionFull | null>(null);
	const [addForm, setAddForm] = useState({ name: '', category_id: '' });
	const [moveTarget, setMoveTarget] = useState('');

	// Роль: 'user' или 'admin'
	const [role] = useState<'user' | 'admin'>(() => {
		return (localStorage.getItem('app_role') as 'user' | 'admin') || 'user';
	});

	// ── Data ──
	const { data: cats = [] } = useQuery({ queryKey: ['categories'], queryFn: categoriesApi.getAll });
	const { data: catParams = [] } = useQuery({
		queryKey: ['cat-params', categoryId],
		queryFn: () => categoryParametersApi.getByCategoryId(Number(categoryId)),
		enabled: !!categoryId,
	});
	// GET /positions — full list (shown before any search is executed)
	const { data: allPositions = [], isLoading: allLoading } = useQuery({
		queryKey: ['positions'],
		queryFn: () => positionsApi.getAll(),
		enabled: !hasSearched,
	});
	const {
		data: results = [],
		isFetching,
		isError,
	} = useQuery({
		queryKey: ['positions-search', searchParams],
		queryFn: () => positionsApi.search(searchParams),
		enabled: hasSearched,
	});

	const catMap = new Map(cats.map((c) => [c.id, c]));
	const flatCats = buildFlatWithPath(cats);

	const getCatPath = (id: number): string => {
		const c = catMap.get(id);
		if (!c) return String(id);
		return c.parent_id === null ? c.name : getCatPath(c.parent_id) + ' / ' + c.name;
	};

	// Known parameter short_names from selected category
	const knownParams = catParams
		.map((cp) => ({ short_name: cp.parameter?.short_name ?? '', name: cp.parameter?.name ?? '' }))
		.filter((p) => p.short_name);

	// ── Filter-row helpers ──
	const addFilterRow = () =>
		setFilterRows((r) => [
			...r,
			{
				uid: `${uid}-${Date.now()}`,
				short_name: knownParams[0]?.short_name ?? '',
				op: 'eq',
				value: '',
			},
		]);

	const updateRow = (uid: string, patch: Partial<FilterRow>) =>
		setFilterRows((r) => r.map((row) => (row.uid === uid ? { ...row, ...patch } : row)));

	const removeRow = (uid: string) => setFilterRows((r) => r.filter((row) => row.uid !== uid));

	const doSearch = () => {
		setSearchParams(buildSearchParams(nameFilter, categoryId, filterRows));
		setHasSearched(true);
	};

	const doReset = () => {
		setNameFilter('');
		setCategoryId('');
		setFilterRows([]);
		setSearchParams({});
		setHasSearched(false);
	};

	// ── Determine result columns ──
	// Union of all short_names appearing in results
	const paramColumns: string[] = [];
	if (results.length > 0) {
		const seen = new Set<string>();
		for (const pos of results) {
			for (const pv of pos.parameters) {
				if (!seen.has(pv.parameter.short_name)) {
					seen.add(pv.parameter.short_name);
					paramColumns.push(pv.parameter.short_name);
				}
			}
		}
	}

	// ── Mutations ──
	const invalidate = () => {
		qc.invalidateQueries({ queryKey: ['positions'] });
		qc.invalidateQueries({ queryKey: ['positions-search'] });
	};

	const createMut = useMutation({
		mutationFn: (d: { name: string; category_id: number }) => positionsApi.create(d),
		onSuccess: (pos) => {
			invalidate();
			setAddModal(false);
			setAddForm({ name: '', category_id: '' });
			toast('Изделие создано', 'success');
			navigate(`/positions/${pos.id}`);
		},
		onError: (e: any) => toast(e?.response?.data?.detail ?? 'Ошибка', 'error'),
	});
	const moveMut = useMutation({
		mutationFn: ({ id, cat }: { id: number; cat: number }) => positionsApi.move(id, cat),
		onSuccess: () => {
			invalidate();
			setMoveModal(null);
			toast('Перемещено', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});
	const deleteMut = useMutation({
		mutationFn: (id: number) => positionsApi.delete(id),
		onSuccess: () => {
			invalidate();
			setDeleteModal(null);
			toast('Удалено', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});

	// ── Parameter filter row renderer ──
	const renderFilterRow = (row: FilterRow) => {
		const paramMeta = catParams.find((cp) => cp.parameter?.short_name === row.short_name);
		const enumTypeId = paramMeta?.parameter?.enum_type_id ?? null;

		return (
			<div
				key={row.uid}
				style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', marginBottom: 6 }}
			>
				{/* short_name selector */}
				<select
					className="form-control"
					style={{ flex: '0 0 160px' }}
					value={row.short_name}
					onChange={(e) => updateRow(row.uid, { short_name: e.target.value, value: '' })}
				>
					<option value="">— параметр —</option>
					{knownParams.map((p) => (
						<option key={p.short_name} value={p.short_name}>
							{p.name} ({p.short_name})
						</option>
					))}
					{/* allow typing a custom short_name if not in list */}
					{row.short_name && !knownParams.find((p) => p.short_name === row.short_name) && (
						<option value={row.short_name}>{row.short_name} (вручную)</option>
					)}
				</select>

				{/* op selector */}
				<select
					className="form-control"
					style={{ flex: '0 0 140px' }}
					value={row.op}
					onChange={(e) => updateRow(row.uid, { op: e.target.value as FilterOp, value: '' })}
				>
					{(Object.entries(OP_LABELS) as [FilterOp, string][]).map(([k, v]) => (
						<option key={k} value={k}>
							{v}
						</option>
					))}
				</select>

				{/* value input */}
				{enumTypeId && row.op === 'eq' ? (
					<EnumValueSelect
						enumTypeId={enumTypeId}
						value={row.value}
						onChange={(v) => updateRow(row.uid, { value: v })}
					/>
				) : row.op === 'min' || row.op === 'max' ? (
					<input
						type="number"
						className="form-control"
						style={{ flex: 1, minWidth: 80 }}
						placeholder="число"
						value={row.value}
						onChange={(e) => updateRow(row.uid, { value: e.target.value })}
					/>
				) : (
					<input
						type="text"
						className="form-control"
						style={{ flex: 1, minWidth: 100 }}
						placeholder="значение"
						value={row.value}
						onChange={(e) => updateRow(row.uid, { value: e.target.value })}
					/>
				)}

				<button
					className="btn btn-ghost btn-icon btn-xs"
					style={{ color: '#ef4444' }}
					onClick={() => removeRow(row.uid)}
				>
					✕
				</button>
			</div>
		);
	};

	return (
		<>
			<div className="page-header">
				<div>
					<div className="page-title">Изделия</div>
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
					+ Новое изделие
				</button>
			</div>

			<div className="page-body" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
				{/* ── Filter card ── */}
				<div className="card">
					<div className="card-header">Фильтры поиска</div>
					<div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
						{/* Primary filters */}
						<div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
							<div className="form-group" style={{ flex: '0 0 260px' }}>
								<label className="form-label">Класс изделия</label>
								<select
									className="form-control"
									value={categoryId}
									onChange={(e) => {
										setCategoryId(e.target.value);
										setFilterRows([]);
									}}
								>
									<option value="">— Все классы —</option>
									{flatCats.map((c) => (
										<option key={c.id} value={c.id}>
											{c.label}
										</option>
									))}
								</select>
							</div>
							<div className="form-group" style={{ flex: 1, minWidth: 180 }}>
								<label className="form-label">Название</label>
								<input
									className="form-control"
									placeholder="Введите название..."
									value={nameFilter}
									onChange={(e) => setNameFilter(e.target.value)}
									onKeyDown={(e) => e.key === 'Enter' && doSearch()}
								/>
							</div>
						</div>

						{/* Parameter filters */}
						{filterRows.length > 0 && (
							<div>
								<div className="form-label" style={{ marginBottom: 8 }}>
									Фильтры по параметрам
								</div>
								{filterRows.map(renderFilterRow)}
							</div>
						)}

						{/* If no category selected but we have filter rows with manual input */}
						{!categoryId && filterRows.length === 0 && (
							<div className="form-hint">
								Выберите класс, чтобы добавить фильтры по значениям параметров
							</div>
						)}

						{/* Actions */}
						<div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
							<button className="btn btn-primary" onClick={doSearch}>
								Найти
							</button>
							{categoryId && (
								<button className="btn btn-secondary" onClick={addFilterRow}>
									+ Добавить фильтр по параметру
								</button>
							)}
							{(nameFilter || categoryId || filterRows.length > 0 || hasSearched) && (
								<button className="btn btn-ghost" onClick={doReset}>
									↺ Сбросить
								</button>
							)}
							{hasSearched && !isFetching && (
								<span className="text-muted" style={{ fontSize: 12, marginLeft: 4 }}>
									Найдено: {results.length}
								</span>
							)}
						</div>
					</div>
				</div>

				{/* ── Results ── */}
				{hasSearched && (
					<div className="card">
						<div className="card-header">
							Результаты
							{!isFetching && <span className="badge badge-gray">{results.length}</span>}
						</div>

						{isFetching && (
							<div className="loading">
								<div className="spinner" />
								Поиск...
							</div>
						)}
						{isError && (
							<div className="empty-state">
								<p className="text-danger">Ошибка запроса</p>
							</div>
						)}

						{!isFetching && !isError && results.length === 0 && (
							<div className="empty-state">
								<p>Изделия не найдены</p>
							</div>
						)}

						{!isFetching && results.length > 0 && (
							<div className="table-wrap">
								<table>
									<thead>
										<tr>
											<th>ID</th>
											<th>Название</th>
											<th>Класс</th>
											{paramColumns.map((sn) => (
												<th key={sn}>{sn}</th>
											))}
											<th>Действия</th>
										</tr>
									</thead>
									<tbody>
										{results.map((pos) => {
											const pvMap = new Map(
												pos.parameters.map((pv) => [pv.parameter.short_name, pv]),
											);
											return (
												<tr key={pos.id}>
													<td className="text-muted font-mono">{pos.id}</td>
													<td style={{ fontWeight: 500 }}>{pos.name}</td>
													<td className="text-muted">{getCatPath(pos.category_id)}</td>
													{paramColumns.map((sn) => (
														<td key={sn}>
															{pvMap.has(sn) ? (
																displayValue(pvMap.get(sn)!)
															) : (
																<span className="text-muted">—</span>
															)}
														</td>
													))}
													<td>
														<div className="td-actions">
															<button
																className="btn btn-secondary btn-xs"
																onClick={() => navigate(`/positions/${pos.id}`)}
															>
																Карточка
															</button>
															<button
																className="btn btn-ghost btn-icon btn-xs"
																title="Переместить"
																onClick={() => {
																	if (role !== 'admin') {
																		return alert('Нет доступа');
																	}

																	setMoveModal({
																		id: pos.id,
																		category_id: pos.category_id,
																		name: pos.name,
																	});
																	setMoveTarget(String(pos.category_id));
																}}
															>
																↕
															</button>
															<button
																className="btn btn-ghost btn-icon btn-xs"
																title="Удалить"
																style={{ color: '#ef4444' }}
																onClick={() => {
																	if (role !== 'admin') {
																		return alert('Нет доступа');
																	}

																	setDeleteModal(pos);
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
				)}

				{!hasSearched && (
					<div className="card">
						<div className="card-header">
							Все изделия
							{!allLoading && <span className="badge badge-gray">{allPositions.length}</span>}
						</div>
						{allLoading && (
							<div className="loading">
								<div className="spinner" /> Загрузка...
							</div>
						)}
						{!allLoading && allPositions.length === 0 && (
							<div className="empty-state">
								<p>Изделий нет. Нажмите «+ Новое изделие» или используйте фильтры выше.</p>
							</div>
						)}
						{!allLoading && allPositions.length > 0 && (
							<div className="table-wrap">
								<table>
									<thead>
										<tr>
											<th>ID</th>
											<th>Название</th>
											<th>Класс</th>
											<th>Действия</th>
										</tr>
									</thead>
									<tbody>
										{allPositions.map((pos) => (
											<tr key={pos.id}>
												<td className="text-muted font-mono">{pos.id}</td>
												<td style={{ fontWeight: 500 }}>{pos.name}</td>
												<td className="text-muted">{getCatPath(pos.category_id)}</td>
												<td>
													<div className="td-actions">
														<button
															className="btn btn-secondary btn-xs"
															onClick={() => navigate(`/positions/${pos.id}`)}
														>
															Карточка
														</button>
														<button
															className="btn btn-ghost btn-icon btn-xs"
															title="Переместить"
															onClick={() => {
																if (role !== 'admin') {
																	return alert('Нет доступа');
																}

																setMoveModal(pos);
																setMoveTarget(String(pos.category_id));
															}}
														>
															↕
														</button>
														<button
															className="btn btn-ghost btn-icon btn-xs"
															title="Удалить"
															style={{ color: '#ef4444' }}
															onClick={() => {
																if (role !== 'admin') {
																	return alert('Нет доступа');
																}

																setDeleteModal({ ...pos, parameters: [] });
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
				)}
			</div>

			{/* ── Add modal ── */}
			<Modal
				open={addModal}
				onClose={() => setAddModal(false)}
				title="Новое изделие"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setAddModal(false)}>
							Отмена
						</button>
						<button
							className="btn btn-primary"
							disabled={!addForm.name.trim() || !addForm.category_id || createMut.isPending}
							onClick={() =>
								createMut.mutate({
									name: addForm.name.trim(),
									category_id: Number(addForm.category_id),
								})
							}
						>
							Создать
						</button>
					</>
				}
			>
				<div className="form-group">
					<label className="form-label">Название</label>
					<input
						className="form-control"
						placeholder="Введите название"
						value={addForm.name}
						onChange={(e) => setAddForm((f) => ({ ...f, name: e.target.value }))}
						autoFocus
					/>
				</div>
				<div className="form-group">
					<label className="form-label">Класс</label>
					<select
						className="form-control"
						value={addForm.category_id}
						onChange={(e) => setAddForm((f) => ({ ...f, category_id: e.target.value }))}
					>
						<option value="">— Выберите класс —</option>
						{flatCats.map((c) => (
							<option key={c.id} value={c.id}>
								{c.label}
							</option>
						))}
					</select>
				</div>
			</Modal>

			{/* ── Move modal ── */}
			<Modal
				open={moveModal !== null}
				onClose={() => setMoveModal(null)}
				title="Переместить изделие"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setMoveModal(null)}>
							Отмена
						</button>
						<button
							className="btn btn-primary"
							disabled={!moveTarget || moveMut.isPending}
							onClick={() => moveModal && moveMut.mutate({ id: moveModal.id, cat: Number(moveTarget) })}
						>
							Переместить
						</button>
					</>
				}
			>
				<p className="text-muted">
					Изделие: <strong>{moveModal?.name}</strong>
				</p>
				<div className="form-group">
					<label className="form-label">Новый класс</label>
					<select className="form-control" value={moveTarget} onChange={(e) => setMoveTarget(e.target.value)}>
						<option value="">— Выберите класс —</option>
						{flatCats.map((c) => (
							<option key={c.id} value={c.id}>
								{c.label}
							</option>
						))}
					</select>
				</div>
			</Modal>

			{/* ── Delete modal ── */}
			<Modal
				open={deleteModal !== null}
				onClose={() => setDeleteModal(null)}
				title="Удалить изделие"
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
					Удалить изделие <strong>«{deleteModal?.name}»</strong>?
				</p>
			</Modal>
		</>
	);
}
