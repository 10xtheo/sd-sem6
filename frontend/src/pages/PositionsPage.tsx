import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { positionsApi } from '../api/positions';
import { categoriesApi } from '../api/categories';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';
import type { Category, Position } from '../types';

function buildFlatWithPath(cats: Category[]): { id: number; label: string }[] {
  const map = new Map<number, Category>();
  for (const c of cats) map.set(c.id, c);

  function getPath(id: number): string {
    const cat = map.get(id);
    if (!cat) return '';
    if (cat.parent_id === null) return cat.name;
    return getPath(cat.parent_id) + ' / ' + cat.name;
  }

  return cats.map(c => ({ id: c.id, label: getPath(c.id) })).sort((a, b) => a.label.localeCompare(b.label));
}

export default function PositionsPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { toast } = useToast();

  const [filterCat, setFilterCat] = useState('');
  const [filterSearch, setFilterSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');

  const [addModal, setAddModal] = useState(false);
  const [moveModal, setMoveModal] = useState<Position | null>(null);
  const [deleteModal, setDeleteModal] = useState<Position | null>(null);
  const [addForm, setAddForm] = useState({ name: '', category_id: '' });
  const [moveTarget, setMoveTarget] = useState('');

  const { data: cats = [] } = useQuery({ queryKey: ['categories'], queryFn: categoriesApi.getAll });
  const { data: positions = [], isLoading } = useQuery({
    queryKey: ['positions', filterCat, filterSearch],
    queryFn: () => positionsApi.getAll({
      category_id: filterCat ? Number(filterCat) : undefined,
      search: filterSearch || undefined,
    }),
  });

  const catMap = new Map(cats.map(c => [c.id, c]));
  const flatCats = buildFlatWithPath(cats);

  const getCatPath = (categoryId: number): string => {
    const cat = catMap.get(categoryId);
    if (!cat) return String(categoryId);
    if (cat.parent_id === null) return cat.name;
    return getCatPath(cat.parent_id) + ' / ' + cat.name;
  };

  const invalidate = () => qc.invalidateQueries({ queryKey: ['positions'] });

  const createMut = useMutation({
    mutationFn: (d: { name: string; category_id: number }) => positionsApi.create(d),
    onSuccess: (pos) => { invalidate(); setAddModal(false); setAddForm({ name: '', category_id: '' }); toast('Изделие создано', 'success'); navigate(`/positions/${pos.id}`); },
    onError: (e: any) => toast(e?.response?.data?.detail ?? 'Ошибка', 'error'),
  });
  const moveMut = useMutation({
    mutationFn: ({ id, cat }: { id: number; cat: number }) => positionsApi.move(id, cat),
    onSuccess: () => { invalidate(); setMoveModal(null); toast('Перемещено', 'success'); },
    onError: () => toast('Ошибка', 'error'),
  });
  const deleteMut = useMutation({
    mutationFn: (id: number) => positionsApi.delete(id),
    onSuccess: () => { invalidate(); setDeleteModal(null); toast('Удалено', 'success'); },
    onError: () => toast('Ошибка', 'error'),
  });

  const doSearch = () => setFilterSearch(searchInput);

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Изделия</div>
          <div className="page-subtitle">Поиск и управление изделиями</div>
        </div>
        <button className="btn btn-primary" onClick={() => setAddModal(true)}>+ Новое изделие</button>
      </div>

      <div className="page-body">
        {/* Filter bar */}
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card-body">
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <div className="form-group" style={{ flex: '0 0 260px' }}>
                <label className="form-label">Класс изделия</label>
                <select className="form-control" value={filterCat} onChange={e => setFilterCat(e.target.value)}>
                  <option value="">— Все классы —</option>
                  {flatCats.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
                </select>
              </div>
              <div className="form-group" style={{ flex: 1, minWidth: 200 }}>
                <label className="form-label">Поиск по названию</label>
                <input className="form-control" placeholder="Введите текст..." value={searchInput}
                  onChange={e => setSearchInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && doSearch()} />
              </div>
              <button className="btn btn-primary" onClick={doSearch}>Найти</button>
              {(filterCat || filterSearch) && (
                <button className="btn btn-secondary" onClick={() => { setFilterCat(''); setFilterSearch(''); setSearchInput(''); }}>
                  Сбросить
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="card">
          <div className="card-header">
            Результаты
            <span className="badge badge-gray">{positions.length}</span>
          </div>
          {isLoading && <div className="loading"><div className="spinner" /> Загрузка...</div>}
          {!isLoading && positions.length === 0 && (
            <div className="empty-state"><div className="empty-icon">📦</div><p>Изделия не найдены</p></div>
          )}
          {positions.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th>ID</th><th>Название</th><th>Класс</th><th>Действия</th></tr>
                </thead>
                <tbody>
                  {positions.map(p => (
                    <tr key={p.id}>
                      <td className="text-muted font-mono">{p.id}</td>
                      <td style={{ fontWeight: 500 }}>{p.name}</td>
                      <td><span className="text-muted">{getCatPath(p.category_id)}</span></td>
                      <td>
                        <div className="td-actions">
                          <button className="btn btn-secondary btn-xs" onClick={() => navigate(`/positions/${p.id}`)}>
                            📝 Карточка
                          </button>
                          <button className="btn btn-ghost btn-icon btn-xs" title="Переместить"
                            onClick={() => { setMoveModal(p); setMoveTarget(String(p.category_id)); }}>↕</button>
                          <button className="btn btn-ghost btn-icon btn-xs" title="Удалить"
                            style={{ color: '#ef4444' }} onClick={() => setDeleteModal(p)}>✕</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Add modal */}
      <Modal open={addModal} onClose={() => setAddModal(false)} title="Новое изделие"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setAddModal(false)}>Отмена</button>
            <button className="btn btn-primary" disabled={!addForm.name.trim() || !addForm.category_id || createMut.isPending}
              onClick={() => createMut.mutate({ name: addForm.name.trim(), category_id: Number(addForm.category_id) })}>
              Создать
            </button>
          </>
        }>
        <div className="form-group">
          <label className="form-label">Название</label>
          <input className="form-control" placeholder="Введите название" value={addForm.name}
            onChange={e => setAddForm(f => ({ ...f, name: e.target.value }))} autoFocus />
        </div>
        <div className="form-group">
          <label className="form-label">Класс</label>
          <select className="form-control" value={addForm.category_id} onChange={e => setAddForm(f => ({ ...f, category_id: e.target.value }))}>
            <option value="">— Выберите класс —</option>
            {flatCats.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
          </select>
        </div>
      </Modal>

      {/* Move modal */}
      <Modal open={moveModal !== null} onClose={() => setMoveModal(null)} title="Переместить изделие"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setMoveModal(null)}>Отмена</button>
            <button className="btn btn-primary" disabled={!moveTarget || moveMut.isPending}
              onClick={() => moveModal && moveMut.mutate({ id: moveModal.id, cat: Number(moveTarget) })}>
              Переместить
            </button>
          </>
        }>
        <p className="text-muted">Изделие: <strong>{moveModal?.name}</strong></p>
        <div className="form-group">
          <label className="form-label">Новый класс</label>
          <select className="form-control" value={moveTarget} onChange={e => setMoveTarget(e.target.value)}>
            <option value="">— Выберите класс —</option>
            {flatCats.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
          </select>
        </div>
      </Modal>

      {/* Delete modal */}
      <Modal open={deleteModal !== null} onClose={() => setDeleteModal(null)} title="Удалить изделие"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setDeleteModal(null)}>Отмена</button>
            <button className="btn btn-danger" disabled={deleteMut.isPending}
              onClick={() => deleteModal && deleteMut.mutate(deleteModal.id)}>
              Удалить
            </button>
          </>
        }>
        <p>Удалить изделие <strong>«{deleteModal?.name}»</strong>?</p>
      </Modal>
    </>
  );
}
