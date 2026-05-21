import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { categoriesApi } from '../api/categories';
import { categoryParametersApi } from '../api/categoryParameters';
import { parametersApi } from '../api/parameters';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';
import type { Category, TreeNode } from '../types';

function buildTree(cats: Category[]): TreeNode[] {
  const map = new Map<number, TreeNode>();
  for (const c of cats) map.set(c.id, { ...c, children: [] });
  const roots: TreeNode[] = [];
  for (const c of cats) {
    if (c.parent_id === null) roots.push(map.get(c.id)!);
    else map.get(c.parent_id)?.children.push(map.get(c.id)!);
  }
  return roots;
}

function TreeNodeItem({
  node, depth, selectedId, onSelect, onAdd, onRename, onDelete, onMove,
}: {
  node: TreeNode; depth: number; selectedId: number | null;
  onSelect: (id: number) => void; onAdd: (parentId: number) => void;
  onRename: (id: number, name: string) => void; onDelete: (id: number, name: string) => void;
  onMove: (id: number, name: string) => void;
}) {
  const [open, setOpen] = useState(true);
  const hasChildren = node.children.length > 0;

  return (
    <div>
      <div
        className={`tree-node-row${selectedId === node.id ? ' selected' : ''}`}
        style={{ paddingLeft: depth * 16 + 8 }}
        onClick={() => onSelect(node.id)}
      >
        <button
          className="tree-toggle"
          onClick={e => { e.stopPropagation(); setOpen(o => !o); }}
          style={{ visibility: hasChildren ? 'visible' : 'hidden' }}
        >
          {open ? '▾' : '▸'}
        </button>
        <span className="tree-label" title={node.name}>{node.name}</span>
        <div className="tree-actions">
          <button className="btn btn-ghost btn-icon btn-xs" title="Добавить дочерний"
            onClick={e => { e.stopPropagation(); onAdd(node.id); }}>+</button>
          <button className="btn btn-ghost btn-icon btn-xs" title="Переименовать"
            onClick={e => { e.stopPropagation(); onRename(node.id, node.name); }}>✏</button>
          <button className="btn btn-ghost btn-icon btn-xs" title="Переместить"
            onClick={e => { e.stopPropagation(); onMove(node.id, node.name); }}>↕</button>
          <button className="btn btn-ghost btn-icon btn-xs" title="Удалить"
            onClick={e => { e.stopPropagation(); onDelete(node.id, node.name); }}
            style={{ color: '#ef4444' }}>✕</button>
        </div>
      </div>
      {open && hasChildren && (
        <div className="tree-children">
          {node.children.map(ch => (
            <TreeNodeItem key={ch.id} node={ch} depth={depth + 1}
              selectedId={selectedId} onSelect={onSelect}
              onAdd={onAdd} onRename={onRename} onDelete={onDelete} onMove={onMove} />
          ))}
        </div>
      )}
    </div>
  );
}


export default function ClassifierPage() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Modals
  const [addModal, setAddModal] = useState<{ open: boolean; parentId: number | null }>({ open: false, parentId: null });
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

  const { data: cats = [], isLoading } = useQuery({ queryKey: ['categories'], queryFn: categoriesApi.getAll });
  const { data: catParams = [], isLoading: paramsLoading } = useQuery({
    queryKey: ['cat-params', selectedId],
    queryFn: () => categoryParametersApi.getByCategoryId(selectedId!),
    enabled: selectedId !== null,
  });
  const { data: allParams = [] } = useQuery({ queryKey: ['parameters'], queryFn: parametersApi.getAll });

  const invalidateCats = () => qc.invalidateQueries({ queryKey: ['categories'] });
  const invalidateCatParams = () => qc.invalidateQueries({ queryKey: ['cat-params', selectedId] });

  const createMut = useMutation({
    mutationFn: (data: { name: string; parent_id: number | null }) => categoriesApi.create(data),
    onSuccess: () => { invalidateCats(); setAddModal({ open: false, parentId: null }); setNewCatName(''); toast('Класс создан', 'success'); },
    onError: () => toast('Ошибка создания', 'error'),
  });
  const renameMut = useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) => categoriesApi.update(id, { name }),
    onSuccess: () => { invalidateCats(); setRenameModal(null); toast('Переименовано', 'success'); },
    onError: () => toast('Ошибка', 'error'),
  });
  const deleteMut = useMutation({
    mutationFn: ({ id, cascade }: { id: number; cascade: boolean }) => categoriesApi.delete(id, cascade),
    onSuccess: () => { invalidateCats(); setDeleteModal(null); if (selectedId === deleteModal?.id) setSelectedId(null); toast('Удалено', 'success'); },
    onError: () => toast('Ошибка удаления', 'error'),
  });
  const moveMut = useMutation({
    mutationFn: ({ id, parentId }: { id: number; parentId: number | null }) => categoriesApi.move(id, parentId),
    onSuccess: () => { invalidateCats(); setMoveModal(null); toast('Перемещено', 'success'); },
    onError: () => toast('Ошибка перемещения', 'error'),
  });
  const addParamMut = useMutation({
    mutationFn: (data: Parameters<typeof categoryParametersApi.add>[0]) => categoryParametersApi.add(data),
    onSuccess: () => { invalidateCatParams(); setAddParamModal(false); setAddParamForm({ parameter_id: '', order_num: '0', min_val: '', max_val: '' }); toast('Параметр добавлен', 'success'); },
    onError: (e: any) => toast(e?.response?.data?.detail ?? 'Ошибка', 'error'),
  });
  const removeParamMut = useMutation({
    mutationFn: ({ catId, paramId }: { catId: number; paramId: number }) => categoryParametersApi.remove(catId, paramId),
    onSuccess: () => { invalidateCatParams(); toast('Параметр удалён', 'success'); },
    onError: () => toast('Ошибка', 'error'),
  });

  const tree = buildTree(cats);
  const selectedCat = cats.find(c => c.id === selectedId);
  const assignedIds = new Set(catParams.map(cp => cp.parameter_id));
  const availableParams = allParams.filter(p => !assignedIds.has(p.id));

  const flatCats = cats.filter(c => c.id !== moveModal?.id);

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Классификатор</div>
          <div className="page-subtitle">Дерево классов изделий и их параметры</div>
        </div>
        <button className="btn btn-primary" onClick={() => setAddModal({ open: true, parentId: null })}>
          + Корневой класс
        </button>
      </div>

      <div className="page-body">
        <div className="split-panel">
          {/* Tree */}
          <div className="split-left card">
            <div className="card-header">
              Дерево классов
              <span className="badge badge-gray">{cats.length}</span>
            </div>
            <div className="tree-scroll">
              {isLoading && <div className="loading"><div className="spinner" /> Загрузка...</div>}
              {!isLoading && tree.length === 0 && (
                <div className="tree-empty">Нет классов.<br />Нажмите «Корневой класс»</div>
              )}
              {tree.map(node => (
                <TreeNodeItem key={node.id} node={node} depth={0}
                  selectedId={selectedId} onSelect={setSelectedId}
                  onAdd={id => { setAddModal({ open: true, parentId: id }); }}
                  onRename={(id, name) => { setRenameModal({ open: true, id, name }); setRenameVal(name); }}
                  onDelete={(id, name) => { setDeleteModal({ open: true, id, name }); setCascade(false); }}
                  onMove={(id, name) => { setMoveModal({ open: true, id, name }); setMoveTarget(''); }}
                />
              ))}
            </div>
          </div>

          {/* Params panel */}
          <div className="split-right card flex-col">
            {selectedCat ? (
              <>
                <div className="card-header">
                  <span>Параметры: <strong>{selectedCat.name}</strong></span>
                  <button className="btn btn-primary btn-xs" onClick={() => setAddParamModal(true)}>
                    + Добавить параметр
                  </button>
                </div>
                <div className="card-body" style={{ flex: 1, overflowY: 'auto', padding: 0 }}>
                  {paramsLoading && <div className="loading"><div className="spinner" /> Загрузка...</div>}
                  {!paramsLoading && catParams.length === 0 && (
                    <div className="empty-state"><div className="empty-icon">📋</div><p>Нет параметров у этого класса</p></div>
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
                            .map(cp => (
                              <tr key={cp.parameter_id}>
                                <td className="text-muted font-mono">{cp.parameter_id}</td>
                                <td>
                                  <div style={{ fontWeight: 500 }}>{cp.parameter?.name ?? '—'}</div>
                                  <div className="text-muted" style={{ fontSize: 12 }}>{cp.parameter?.short_name}</div>
                                </td>
                                <td>{cp.order_num}</td>
                                <td>{cp.min_val ?? <span className="text-muted">—</span>}</td>
                                <td>{cp.max_val ?? <span className="text-muted">—</span>}</td>
                                <td>
                                  <button className="btn btn-ghost btn-icon btn-xs" title="Удалить"
                                    style={{ color: '#ef4444' }}
                                    onClick={() => removeParamMut.mutate({ catId: selectedId!, paramId: cp.parameter_id })}>
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
              <div className="empty-state" style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <div className="empty-icon">👈</div>
                <p>Выберите класс в дереве слева<br />для управления его параметрами</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add category modal */}
      <Modal open={addModal.open} onClose={() => setAddModal({ open: false, parentId: null })} title={addModal.parentId ? 'Добавить дочерний класс' : 'Добавить корневой класс'}
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setAddModal({ open: false, parentId: null })}>Отмена</button>
            <button className="btn btn-primary" disabled={!newCatName.trim() || createMut.isPending}
              onClick={() => createMut.mutate({ name: newCatName.trim(), parent_id: addModal.parentId })}>
              Создать
            </button>
          </>
        }>
        {addModal.parentId && (
          <div className="form-hint">Родительский класс: <strong>{cats.find(c => c.id === addModal.parentId)?.name}</strong></div>
        )}
        <div className="form-group">
          <label className="form-label">Название</label>
          <input className="form-control" placeholder="Введите название класса"
            value={newCatName} onChange={e => setNewCatName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && newCatName.trim() && createMut.mutate({ name: newCatName.trim(), parent_id: addModal.parentId })} autoFocus />
        </div>
      </Modal>

      {/* Rename modal */}
      <Modal open={renameModal?.open ?? false} onClose={() => setRenameModal(null)} title="Переименовать класс"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setRenameModal(null)}>Отмена</button>
            <button className="btn btn-primary" disabled={!renameVal.trim() || renameMut.isPending}
              onClick={() => renameModal && renameMut.mutate({ id: renameModal.id, name: renameVal.trim() })}>
              Сохранить
            </button>
          </>
        }>
        <div className="form-group">
          <label className="form-label">Новое название</label>
          <input className="form-control" value={renameVal} onChange={e => setRenameVal(e.target.value)} autoFocus />
        </div>
      </Modal>

      {/* Delete modal */}
      <Modal open={deleteModal?.open ?? false} onClose={() => setDeleteModal(null)} title="Удалить класс"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setDeleteModal(null)}>Отмена</button>
            <button className="btn btn-danger" disabled={deleteMut.isPending}
              onClick={() => deleteModal && deleteMut.mutate({ id: deleteModal.id, cascade })}>
              Удалить
            </button>
          </>
        }>
        <p>Удалить класс <strong>«{deleteModal?.name}»</strong>?</p>
        <label style={{ display: 'flex', gap: 8, alignItems: 'center', cursor: 'pointer' }}>
          <input type="checkbox" checked={cascade} onChange={e => setCascade(e.target.checked)} />
          <span>Удалить вместе со всеми дочерними классами</span>
        </label>
      </Modal>

      {/* Move modal */}
      <Modal open={moveModal?.open ?? false} onClose={() => setMoveModal(null)} title="Переместить класс"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setMoveModal(null)}>Отмена</button>
            <button className="btn btn-primary" disabled={moveMut.isPending}
              onClick={() => moveModal && moveMut.mutate({ id: moveModal.id, parentId: moveTarget === '' ? null : Number(moveTarget) })}>
              Переместить
            </button>
          </>
        }>
        <p className="text-muted">Перемещаем: <strong>{moveModal?.name}</strong></p>
        <div className="form-group">
          <label className="form-label">Новый родительский класс</label>
          <select className="form-control" value={moveTarget} onChange={e => setMoveTarget(e.target.value)}>
            <option value="">— Корень (без родителя) —</option>
            {flatCats.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
      </Modal>

      {/* Add param modal */}
      <Modal open={addParamModal} onClose={() => setAddParamModal(false)} title={`Добавить параметр → ${selectedCat?.name}`}
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setAddParamModal(false)}>Отмена</button>
            <button className="btn btn-primary"
              disabled={!addParamForm.parameter_id || addParamMut.isPending}
              onClick={() => selectedId && addParamMut.mutate({
                category_id: selectedId,
                parameter_id: Number(addParamForm.parameter_id),
                order_num: Number(addParamForm.order_num) || 0,
                min_val: addParamForm.min_val !== '' ? Number(addParamForm.min_val) : null,
                max_val: addParamForm.max_val !== '' ? Number(addParamForm.max_val) : null,
              })}>
              Добавить
            </button>
          </>
        }>
        <div className="form-group">
          <label className="form-label">Параметр</label>
          <select className="form-control" value={addParamForm.parameter_id}
            onChange={e => setAddParamForm(f => ({ ...f, parameter_id: e.target.value }))}>
            <option value="">— Выберите параметр —</option>
            {availableParams.map(p => <option key={p.id} value={p.id}>{p.name} ({p.short_name})</option>)}
          </select>
          {availableParams.length === 0 && (
            <span className="form-hint">Все параметры уже добавлены. Создайте новые в разделе «Параметры».</span>
          )}
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Порядок вывода</label>
            <input type="number" className="form-control" value={addParamForm.order_num}
              onChange={e => setAddParamForm(f => ({ ...f, order_num: e.target.value }))} />
          </div>
          <div className="form-group">
            <label className="form-label">Мин. значение</label>
            <input type="number" className="form-control" placeholder="—" value={addParamForm.min_val}
              onChange={e => setAddParamForm(f => ({ ...f, min_val: e.target.value }))} />
          </div>
          <div className="form-group">
            <label className="form-label">Макс. значение</label>
            <input type="number" className="form-control" placeholder="—" value={addParamForm.max_val}
              onChange={e => setAddParamForm(f => ({ ...f, max_val: e.target.value }))} />
          </div>
        </div>
      </Modal>
    </>
  );
}
