import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { unitsApi } from '../api/units';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';
import type { Unit } from '../types';

export default function UnitsPage() {
  const qc = useQueryClient();
  const { toast } = useToast();

  const [addModal, setAddModal] = useState(false);
  const [editModal, setEditModal] = useState<Unit | null>(null);
  const [deleteModal, setDeleteModal] = useState<Unit | null>(null);
  const [form, setForm] = useState({ code: '', name: '', symbol: '' });

  const { data: units = [], isLoading } = useQuery({ queryKey: ['units'], queryFn: unitsApi.getAll });
  // GET /units/{id} — fetch fresh unit data when editing
  const { data: editingUnitDetail } = useQuery({
    queryKey: ['unit', editModal?.id],
    queryFn: () => unitsApi.getById(editModal!.id),
    enabled: !!editModal,
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ['units'] });

  const openAdd = () => { setForm({ code: '', name: '', symbol: '' }); setAddModal(true); };
  const openEdit = (u: Unit) => { setForm({ code: u.code, name: u.name, symbol: u.symbol }); setEditModal(u); };

  const createMut = useMutation({
    mutationFn: () => unitsApi.create({ code: form.code.trim(), name: form.name.trim(), symbol: form.symbol.trim() }),
    onSuccess: () => { invalidate(); setAddModal(false); toast('Единица создана', 'success'); },
    onError: () => toast('Ошибка', 'error'),
  });

  const updateMut = useMutation({
    mutationFn: ({ id }: { id: number }) => unitsApi.update(id, { code: form.code.trim(), name: form.name.trim(), symbol: form.symbol.trim() }),
    onSuccess: () => { invalidate(); setEditModal(null); toast('Обновлено', 'success'); },
    onError: () => toast('Ошибка', 'error'),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => unitsApi.delete(id),
    onSuccess: () => { invalidate(); setDeleteModal(null); toast('Удалено', 'success'); },
    onError: () => toast('Ошибка', 'error'),
  });

  const UnitForm = (
    <>
      <div className="form-row">
        <div className="form-group" style={{ flex: '0 0 120px' }}>
          <label className="form-label">Код</label>
          <input className="form-control font-mono" value={form.code} placeholder="kg"
            onChange={e => setForm(f => ({ ...f, code: e.target.value }))} autoFocus />
        </div>
        <div className="form-group" style={{ flex: '0 0 80px' }}>
          <label className="form-label">Символ</label>
          <input className="form-control" value={form.symbol} placeholder="кг"
            onChange={e => setForm(f => ({ ...f, symbol: e.target.value }))} />
        </div>
        <div className="form-group">
          <label className="form-label">Название</label>
          <input className="form-control" value={form.name} placeholder="Килограммы"
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
        </div>
      </div>
    </>
  );

  const isValid = form.code.trim() && form.name.trim() && form.symbol.trim();

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Единицы измерения</div>
        </div>
        <button className="btn btn-primary" onClick={openAdd}>+ Добавить</button>
      </div>

      <div className="page-body">
        <div className="card">
          <div className="card-header">
            Единицы измерения
            <span className="badge badge-gray">{units.length}</span>
          </div>
          {isLoading && <div className="loading"><div className="spinner" /> Загрузка...</div>}
          {!isLoading && units.length === 0 && (
            <div className="empty-state"><p>Нет единиц измерения</p></div>
          )}
          {units.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th>ID</th><th>Код</th><th>Символ</th><th>Название</th><th></th></tr>
                </thead>
                <tbody>
                  {units.map(u => (
                    <tr key={u.id}>
                      <td className="text-muted font-mono">{u.id}</td>
                      <td><span className="font-mono badge badge-gray">{u.code}</span></td>
                      <td style={{ fontWeight: 700 }}>{u.symbol}</td>
                      <td>{u.name}</td>
                      <td>
                        <div className="td-actions">
                          <button className="btn btn-ghost btn-icon btn-xs" title="Редактировать" onClick={() => openEdit(u)}>✏</button>
                          <button className="btn btn-ghost btn-icon btn-xs" title="Удалить" style={{ color: '#ef4444' }} onClick={() => setDeleteModal(u)}>✕</button>
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

      <Modal open={addModal} onClose={() => setAddModal(false)} title="Новая единица"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setAddModal(false)}>Отмена</button>
            <button className="btn btn-primary" disabled={!isValid || createMut.isPending} onClick={() => createMut.mutate()}>Создать</button>
          </>
        }>
        {UnitForm}
      </Modal>

      <Modal open={editModal !== null} onClose={() => setEditModal(null)}
        title={`Редактировать единицу${editingUnitDetail ? ` — ID ${editingUnitDetail.id}` : ''}`}
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setEditModal(null)}>Отмена</button>
            <button className="btn btn-primary" disabled={!isValid || updateMut.isPending}
              onClick={() => editModal && updateMut.mutate({ id: editModal.id })}>Сохранить</button>
          </>
        }>
        {UnitForm}
      </Modal>

      <Modal open={deleteModal !== null} onClose={() => setDeleteModal(null)} title="Удалить единицу"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setDeleteModal(null)}>Отмена</button>
            <button className="btn btn-danger" disabled={deleteMut.isPending}
              onClick={() => deleteModal && deleteMut.mutate(deleteModal.id)}>Удалить</button>
          </>
        }>
        <p>Удалить единицу <strong>«{deleteModal?.name}»</strong> ({deleteModal?.symbol})?</p>
      </Modal>
    </>
  );
}
