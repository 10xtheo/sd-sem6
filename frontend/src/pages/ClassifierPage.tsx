import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { categoriesApi } from '../api/categories';
import { categoryParametersApi } from '../api/categoryParameters';
import { parametersApi } from '../api/parameters';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';
import type { TreeCatItem, TreePosItem } from '../api/categories';

// ─── Tree types ──────────────────────────────────────────────────────────────

type RawItem = TreeCatItem | TreePosItem;

type TreeCatNode = TreeCatItem & { children: TreeAnyNode[] };
type TreeAnyNode = TreeCatNode | TreePosItem;

function buildTreeFromItems(items: RawItem[]): TreeCatNode[] {
	const roots: TreeCatNode[] = [];
	const stack: { node: TreeCatNode; level: number }[] = [];

	for (const item of items) {
		// Pop stack items whose level is >= current item's level
		while (stack.length > 0 && stack[stack.length - 1].level >= item.level) stack.pop();

		if (item.type === 'category') {
			const node: TreeCatNode = { ...item, children: [] };
			if (stack.length === 0) roots.push(node);
			else stack[stack.length - 1].node.children.push(node);
			stack.push({ node, level: item.level });
		} else {
			// position — leaf, add to current stack top
			if (stack.length > 0) stack[stack.length - 1].node.children.push(item);
		}
	}
	return roots;
}

// ─── Tree node component ─────────────────────────────────────────────────────

function TreeCategoryNode({
	node,
	selectedId,
	onSelect,
	onAdd,
	onRename,
	onDelete,
	onMove,
	onNavigate,
}: {
	node: TreeAnyNode;
	selectedId: number | null;
	onSelect: (id: number) => void;
	onAdd: (parentId: number) => void;
	onRename: (id: number, name: string) => void;
	onDelete: (id: number, name: string) => void;
	onMove: (id: number, name: string) => void;
	onNavigate: (posId: number) => void;
}) {
	const [open, setOpen] = useState(true);

	// Роль: 'user' или 'admin'
	const [role] = useState<'user' | 'admin'>(() => {
		return (localStorage.getItem('app_role') as 'user' | 'admin') || 'user';
	});

	if (node.type === 'position') {
		return (
			<div className="tree-node-row" style={{ paddingLeft: 24, opacity: 0.85 }}>
				<span className="tree-label" style={{ fontSize: 12, color: 'var(--text-muted)' }} title={node.name}>
					{node.name}
				</span>
				<div className="tree-actions">
					<button
						className="btn btn-ghost btn-xs"
						title="Открыть карточку"
						onClick={(e) => {
							e.stopPropagation();
							onNavigate(node.id);
						}}
						style={{ fontSize: 11 }}
					>
						↗
					</button>
				</div>
			</div>
		);
	}

	const hasChildren = node.children.length > 0;

	return (
		<div>
			<div
				className={`tree-node-row${selectedId === node.id ? ' selected' : ''}`}
				style={{ paddingLeft: node.level * 16 + 8 }}
				onClick={() => onSelect(node.id)}
			>
				<button
					className="tree-toggle"
					onClick={(e) => {
						e.stopPropagation();
						setOpen((o) => !o);
					}}
					style={{ visibility: hasChildren ? 'visible' : 'hidden' }}
				>
					{open ? '▾' : '▸'}
				</button>
				<span className="tree-label" title={node.name}>
					{node.name}
				</span>
				<div className="tree-actions">
					<button
						className="btn btn-ghost btn-icon btn-xs"
						title="Добавить дочерний"
						onClick={(e) => {
							if (role !== 'admin') {
								return alert('Нет доступа');
							}

							e.stopPropagation();
							onAdd(node.id);
						}}
					>
						+
					</button>
					<button
						className="btn btn-ghost btn-icon btn-xs"
						title="Переименовать"
						onClick={(e) => {
							if (role !== 'admin') {
								return alert('Нет доступа');
							}

							e.stopPropagation();
							onRename(node.id, node.name);
						}}
					>
						✏
					</button>
					<button
						className="btn btn-ghost btn-icon btn-xs"
						title="Переместить"
						onClick={(e) => {
							if (role !== 'admin') {
								return alert('Нет доступа');
							}

							e.stopPropagation();
							onMove(node.id, node.name);
						}}
					>
						↕
					</button>
					<button
						className="btn btn-ghost btn-icon btn-xs"
						title="Удалить"
						style={{ color: '#ef4444' }}
						onClick={(e) => {
							if (role !== 'admin') {
								return alert('Нет доступа');
							}

							e.stopPropagation();
							onDelete(node.id, node.name);
						}}
					>
						✕
					</button>
				</div>
			</div>
			{open &&
				hasChildren &&
				node.children.map((child) => (
					<div key={`${child.type}-${child.id}`} style={{ marginLeft: 16 }}>
						<TreeCategoryNode
							node={child}
							selectedId={selectedId}
							onSelect={onSelect}
							onAdd={onAdd}
							onRename={onRename}
							onDelete={onDelete}
							onMove={onMove}
							onNavigate={onNavigate}
						/>
					</div>
				))}
		</div>
	);
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function ClassifierPage() {
	const qc = useQueryClient();
	const navigate = useNavigate();
	const { toast } = useToast();
	const [selectedId, setSelectedId] = useState<number | null>(null);

	// Modals
	const [addModal, setAddModal] = useState<{ open: boolean; parentId: number | null }>({
		open: false,
		parentId: null,
	});
	const [renameModal, setRenameModal] = useState<{ open: boolean; id: number; name: string } | null>(null);
	const [deleteModal, setDeleteModal] = useState<{ open: boolean; id: number; name: string } | null>(null);
	const [moveModal, setMoveModal] = useState<{ open: boolean; id: number; name: string } | null>(null);
	const [addParamModal, setAddParamModal] = useState(false);

	// Form state
	const [newCatName, setNewCatName] = useState('');
	const [renameVal, setRenameVal] = useState('');
	const [moveTarget, setMoveTarget] = useState<string>('');
	const [cascade, setCascade] = useState(false);
	const [addParamForm, setAddParamForm] = useState({ parameter_id: '', order_num: '0', min_val: '', max_val: '' });

	// Роль: 'user' или 'admin'
	const [role] = useState<'user' | 'admin'>(() => {
		return (localStorage.getItem('app_role') as 'user' | 'admin') || 'user';
	});

	// ── Data queries ──
	// Full tree (categories + positions) — covers GET /categories/tree
	const { data: treeData, isLoading: treeLoading } = useQuery({
		queryKey: ['categories-tree'],
		queryFn: () => categoriesApi.getTree(),
	});

	// Flat categories list — for move dropdowns and lookup
	const { data: cats = [] } = useQuery({ queryKey: ['categories'], queryFn: categoriesApi.getAll });

	// Selected category detail — covers GET /categories/{id}
	const { data: selectedCatDetail } = useQuery({
		queryKey: ['cat-detail', selectedId],
		queryFn: () => categoriesApi.getById(selectedId!),
		enabled: selectedId !== null,
	});

	// Direct children count — covers GET /categories/{id}/children
	const { data: selectedChildren = [] } = useQuery({
		queryKey: ['cat-children', selectedId],
		queryFn: () => categoriesApi.getChildren(selectedId!),
		enabled: selectedId !== null,
	});

	// All descendants count — covers GET /categories/{id}/descendants
	const { data: selectedDescendants = [] } = useQuery({
		queryKey: ['cat-descendants', selectedId],
		queryFn: () => categoriesApi.getDescendants(selectedId!),
		enabled: selectedId !== null,
	});

	// Selected category parents breadcrumb — covers GET /categories/{id}/parents
	const { data: selectedParents = [] } = useQuery({
		queryKey: ['cat-parents', selectedId],
		queryFn: () => categoriesApi.getParents(selectedId!),
		enabled: selectedId !== null,
	});

	const { data: catParams = [], isLoading: paramsLoading } = useQuery({
		queryKey: ['cat-params', selectedId],
		queryFn: () => categoryParametersApi.getByCategoryId(selectedId!),
		enabled: selectedId !== null,
	});
	const { data: allParams = [] } = useQuery({ queryKey: ['parameters'], queryFn: parametersApi.getAll });

	const invalidateCats = () => {
		qc.invalidateQueries({ queryKey: ['categories'] });
		qc.invalidateQueries({ queryKey: ['categories-tree'] });
	};
	const invalidateCatParams = () => qc.invalidateQueries({ queryKey: ['cat-params', selectedId] });

	// ── Mutations ──
	const createMut = useMutation({
		mutationFn: (data: { name: string; parent_id: number | null }) => categoriesApi.create(data),
		onSuccess: () => {
			invalidateCats();
			setAddModal({ open: false, parentId: null });
			setNewCatName('');
			toast('Класс создан', 'success');
		},
		onError: () => toast('Ошибка создания', 'error'),
	});
	const renameMut = useMutation({
		mutationFn: ({ id, name }: { id: number; name: string }) => categoriesApi.update(id, { name }),
		onSuccess: () => {
			invalidateCats();
			setRenameModal(null);
			toast('Переименовано', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});
	const deleteMut = useMutation({
		mutationFn: ({ id, cascade }: { id: number; cascade: boolean }) => categoriesApi.delete(id, cascade),
		onSuccess: () => {
			invalidateCats();
			setDeleteModal(null);
			if (selectedId === deleteModal?.id) setSelectedId(null);
			toast('Удалено', 'success');
		},
		onError: () => toast('Ошибка удаления', 'error'),
	});
	const moveMut = useMutation({
		mutationFn: ({ id, parentId }: { id: number; parentId: number | null }) => categoriesApi.move(id, parentId),
		onSuccess: () => {
			invalidateCats();
			setMoveModal(null);
			toast('Перемещено', 'success');
		},
		onError: () => toast('Ошибка перемещения', 'error'),
	});
	const addParamMut = useMutation({
		mutationFn: (data: Parameters<typeof categoryParametersApi.add>[0]) => categoryParametersApi.add(data),
		onSuccess: () => {
			invalidateCatParams();
			setAddParamModal(false);
			setAddParamForm({ parameter_id: '', order_num: '0', min_val: '', max_val: '' });
			toast('Параметр добавлен', 'success');
		},
		onError: (e: any) => toast(e?.response?.data?.detail ?? 'Ошибка', 'error'),
	});
	const removeParamMut = useMutation({
		mutationFn: ({ catId, paramId }: { catId: number; paramId: number }) =>
			categoryParametersApi.remove(catId, paramId),
		onSuccess: () => {
			invalidateCatParams();
			toast('Параметр удалён', 'success');
		},
		onError: () => toast('Ошибка', 'error'),
	});

	// ── Derived ──
	const treeNodes = buildTreeFromItems((treeData?.items ?? []) as RawItem[]);
	const selectedCat = cats.find((c) => c.id === selectedId);
	const assignedIds = new Set(catParams.map((cp) => cp.parameter_id));
	const availableParams = allParams.filter((p) => !assignedIds.has(p.id));
	const flatCats = cats.filter((c) => c.id !== moveModal?.id);

	// Breadcrumb string for selected category
	const breadcrumb =
		selectedParents.length > 0
			? [...selectedParents]
					.reverse()
					.map((p) => p.name)
					.join(' / ') + (selectedCat ? ' / ' + selectedCat.name : '')
			: (selectedCat?.name ?? '');

	return (
		<>
			<div className="page-header">
				<div>
					<div className="page-title">Классификатор</div>
				</div>
				<button
					className="btn btn-primary"
					onClick={() => {
						if (role !== 'admin') {
							return alert('Нет доступа');
						}

						setAddModal({ open: true, parentId: null });
					}}
				>
					+ Корневой класс
				</button>
			</div>

			<div className="page-body">
				<div className="split-panel">
					{/* ── Tree ── */}
					<div className="split-left card">
						<div className="card-header">
							Дерево классов
							<span className="badge badge-gray">{cats.length}</span>
						</div>
						<div className="tree-scroll">
							{treeLoading && (
								<div className="loading">
									<div className="spinner" /> Загрузка...
								</div>
							)}
							{!treeLoading && treeNodes.length === 0 && (
								<div className="tree-empty">Нет классов. Нажмите «Корневой класс».</div>
							)}
							{treeNodes.map((node) => (
								<TreeCategoryNode
									key={node.id}
									node={node}
									selectedId={selectedId}
									onSelect={setSelectedId}
									onAdd={(id) => setAddModal({ open: true, parentId: id })}
									onRename={(id, name) => {
										setRenameModal({ open: true, id, name });
										setRenameVal(name);
									}}
									onDelete={(id, name) => {
										setDeleteModal({ open: true, id, name });
										setCascade(false);
									}}
									onMove={(id, name) => {
										setMoveModal({ open: true, id, name });
										setMoveTarget('');
									}}
									onNavigate={(posId) => navigate(`/positions/${posId}`)}
								/>
							))}
						</div>
					</div>

					{/* ── Right: param editor ── */}
					<div className="split-right card flex-col">
						{selectedCat ? (
							<>
								<div className="card-header">
									<div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
										<span>
											Параметры: <strong>{selectedCatDetail?.name ?? selectedCat.name}</strong>
											<span className="badge badge-gray" style={{ marginLeft: 6, fontSize: 10 }}>
												ID {selectedCat.id}
											</span>
										</span>
										{breadcrumb && (
											<span className="text-muted" style={{ fontSize: 11, fontWeight: 400 }}>
												{breadcrumb}
											</span>
										)}
										<span className="text-muted" style={{ fontSize: 11, fontWeight: 400 }}>
											Дочерних: {selectedChildren.length} · Потомков: {selectedDescendants.length}
										</span>
									</div>
									<button
										className="btn btn-primary btn-xs"
										onClick={() => {
											if (role !== 'admin') {
												return alert('Нет доступа');
											}

											setAddParamModal(true);
										}}
									>
										+ Добавить параметр
									</button>
								</div>
								<div className="card-body" style={{ flex: 1, overflowY: 'auto', padding: 0 }}>
									{paramsLoading && (
										<div className="loading">
											<div className="spinner" /> Загрузка...
										</div>
									)}
									{!paramsLoading && catParams.length === 0 && (
										<div className="empty-state">
											<p>Нет параметров у этого класса</p>
										</div>
									)}
									{catParams.length > 0 && (
										<div className="table-wrap">
											<table>
												<thead>
													<tr>
														<th>#</th>
														<th>Параметр</th>
														<th>Порядок</th>
														<th>Мин</th>
														<th>Макс</th>
														<th></th>
													</tr>
												</thead>
												<tbody>
													{[...catParams]
														.sort((a, b) => a.order_num - b.order_num)
														.map((cp) => (
															<tr key={cp.parameter_id}>
																<td className="text-muted font-mono">
																	{cp.parameter_id}
																</td>
																<td>
																	<div style={{ fontWeight: 500 }}>
																		{cp.parameter?.name ?? '—'}
																	</div>
																	<div
																		className="text-muted"
																		style={{ fontSize: 12 }}
																	>
																		{cp.parameter?.short_name}
																	</div>
																</td>
																<td>{cp.order_num}</td>
																<td>
																	{cp.min_val ?? (
																		<span className="text-muted">—</span>
																	)}
																</td>
																<td>
																	{cp.max_val ?? (
																		<span className="text-muted">—</span>
																	)}
																</td>
																<td>
																	<button
																		className="btn btn-ghost btn-icon btn-xs"
																		style={{ color: '#ef4444' }}
																		onClick={() => {
																			if (role !== 'admin') {
																				return alert('Нет доступа');
																			}

																			removeParamMut.mutate({
																				catId: selectedId!,
																				paramId: cp.parameter_id,
																			});
																		}}
																	>
																		✕
																	</button>
																</td>
															</tr>
														))}
												</tbody>
											</table>
										</div>
									)}
								</div>
							</>
						) : (
							<div
								className="empty-state"
								style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
							>
								<p>
									Выберите класс в дереве
									<br />
									для управления его параметрами
								</p>
							</div>
						)}
					</div>
				</div>
			</div>

			{/* ── Modals ── */}
			<Modal
				open={addModal.open}
				onClose={() => setAddModal({ open: false, parentId: null })}
				title={addModal.parentId ? 'Добавить дочерний класс' : 'Добавить корневой класс'}
				footer={
					<>
						<button
							className="btn btn-secondary"
							onClick={() => setAddModal({ open: false, parentId: null })}
						>
							Отмена
						</button>
						<button
							className="btn btn-primary"
							disabled={!newCatName.trim() || createMut.isPending}
							onClick={() => createMut.mutate({ name: newCatName.trim(), parent_id: addModal.parentId })}
						>
							Создать
						</button>
					</>
				}
			>
				{addModal.parentId && (
					<div className="form-hint">
						Родитель: <strong>{cats.find((c) => c.id === addModal.parentId)?.name}</strong>
					</div>
				)}
				<div className="form-group">
					<label className="form-label">Название</label>
					<input
						className="form-control"
						placeholder="Введите название класса"
						value={newCatName}
						onChange={(e) => setNewCatName(e.target.value)}
						onKeyDown={(e) =>
							e.key === 'Enter' &&
							newCatName.trim() &&
							createMut.mutate({ name: newCatName.trim(), parent_id: addModal.parentId })
						}
						autoFocus
					/>
				</div>
			</Modal>

			<Modal
				open={renameModal?.open ?? false}
				onClose={() => setRenameModal(null)}
				title="Переименовать класс"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setRenameModal(null)}>
							Отмена
						</button>
						<button
							className="btn btn-primary"
							disabled={!renameVal.trim() || renameMut.isPending}
							onClick={() =>
								renameModal && renameMut.mutate({ id: renameModal.id, name: renameVal.trim() })
							}
						>
							Сохранить
						</button>
					</>
				}
			>
				<div className="form-group">
					<label className="form-label">Новое название</label>
					<input
						className="form-control"
						value={renameVal}
						onChange={(e) => setRenameVal(e.target.value)}
						autoFocus
					/>
				</div>
			</Modal>

			<Modal
				open={deleteModal?.open ?? false}
				onClose={() => setDeleteModal(null)}
				title="Удалить класс"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setDeleteModal(null)}>
							Отмена
						</button>
						<button
							className="btn btn-danger"
							disabled={deleteMut.isPending}
							onClick={() => deleteModal && deleteMut.mutate({ id: deleteModal.id, cascade })}
						>
							Удалить
						</button>
					</>
				}
			>
				<p>
					Удалить класс <strong>«{deleteModal?.name}»</strong>?
				</p>
				<label style={{ display: 'flex', gap: 8, alignItems: 'center', cursor: 'pointer', marginTop: 10 }}>
					<input type="checkbox" checked={cascade} onChange={(e) => setCascade(e.target.checked)} />
					Удалить вместе со всеми дочерними классами
				</label>
			</Modal>

			<Modal
				open={moveModal?.open ?? false}
				onClose={() => setMoveModal(null)}
				title="Переместить класс"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setMoveModal(null)}>
							Отмена
						</button>
						<button
							className="btn btn-primary"
							disabled={moveMut.isPending}
							onClick={() =>
								moveModal &&
								moveMut.mutate({
									id: moveModal.id,
									parentId: moveTarget === '' ? null : Number(moveTarget),
								})
							}
						>
							Переместить
						</button>
					</>
				}
			>
				<p className="text-muted">
					Перемещаем: <strong>{moveModal?.name}</strong>
				</p>
				<div className="form-group">
					<label className="form-label">Новый родительский класс</label>
					<select className="form-control" value={moveTarget} onChange={(e) => setMoveTarget(e.target.value)}>
						<option value="">— Корень (без родителя) —</option>
						{flatCats.map((c) => (
							<option key={c.id} value={c.id}>
								{c.name}
							</option>
						))}
					</select>
				</div>
			</Modal>

			<Modal
				open={addParamModal}
				onClose={() => setAddParamModal(false)}
				title={`Добавить параметр → ${selectedCat?.name}`}
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setAddParamModal(false)}>
							Отмена
						</button>
						<button
							className="btn btn-primary"
							disabled={!addParamForm.parameter_id || addParamMut.isPending}
							onClick={() =>
								selectedId &&
								addParamMut.mutate({
									category_id: selectedId,
									parameter_id: Number(addParamForm.parameter_id),
									order_num: Number(addParamForm.order_num) || 0,
									min_val: addParamForm.min_val !== '' ? Number(addParamForm.min_val) : null,
									max_val: addParamForm.max_val !== '' ? Number(addParamForm.max_val) : null,
								})
							}
						>
							Добавить
						</button>
					</>
				}
			>
				<div className="form-group">
					<label className="form-label">Параметр</label>
					<select
						className="form-control"
						value={addParamForm.parameter_id}
						onChange={(e) => setAddParamForm((f) => ({ ...f, parameter_id: e.target.value }))}
					>
						<option value="">— Выберите параметр —</option>
						{availableParams.map((p) => (
							<option key={p.id} value={p.id}>
								{p.name} ({p.short_name})
							</option>
						))}
					</select>
					{availableParams.length === 0 && <span className="form-hint">Все параметры уже добавлены.</span>}
				</div>
				<div className="form-row">
					<div className="form-group">
						<label className="form-label">Порядок вывода</label>
						<input
							type="number"
							className="form-control"
							value={addParamForm.order_num}
							onChange={(e) => setAddParamForm((f) => ({ ...f, order_num: e.target.value }))}
						/>
					</div>
					<div className="form-group">
						<label className="form-label">Мин</label>
						<input
							type="number"
							className="form-control"
							placeholder="—"
							value={addParamForm.min_val}
							onChange={(e) => setAddParamForm((f) => ({ ...f, min_val: e.target.value }))}
						/>
					</div>
					<div className="form-group">
						<label className="form-label">Макс</label>
						<input
							type="number"
							className="form-control"
							placeholder="—"
							value={addParamForm.max_val}
							onChange={(e) => setAddParamForm((f) => ({ ...f, max_val: e.target.value }))}
						/>
					</div>
				</div>
			</Modal>
		</>
	);
}
