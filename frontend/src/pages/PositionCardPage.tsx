import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { positionsApi } from '../api/positions';
import { enumsApi } from '../api/enums';
import { positionParametersApi } from '../api/positionParameters';
import { useToast } from '../components/Toast';
import type { ParameterValue } from '../types';

const TYPE_LABELS: Record<string, string> = {
  real: 'Вещественное', integer: 'Целое', string: 'Строка', datetime: 'Дата/время', enum: 'Перечисление',
};

function typeClass(code: string | null | undefined) {
  return `badge type-${code ?? 'gray'}`;
}

function EnumSelect({ enumTypeId, value, onChange }: { enumTypeId: number; value: number | null; onChange: (id: number | null) => void }) {
  const { data: values = [] } = useQuery({
    queryKey: ['enum-values', enumTypeId],
    queryFn: () => enumsApi.getTypeValues(enumTypeId),
  });
  return (
    <select className="form-control"
      value={value ?? ''}
      onChange={e => onChange(e.target.value === '' ? null : Number(e.target.value))}>
      <option value="">— Не задано —</option>
      {[...values].sort((a, b) => a.order_number - b.order_number).map(v => (
        <option key={v.id} value={v.id}>{v.name}{v.code ? ` (${v.code})` : ''}</option>
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
    case 'real':     return { val_real: state.val_real !== '' ? Number(state.val_real) : null };
    case 'integer':  return { val_int: state.val_int !== '' ? Number(state.val_int) : null };
    case 'string':   return { val_str: state.val_str || null };
    case 'datetime': return { val_dt: state.val_dt || null };
    case 'enum':     return { enum_val_id: state.enum_val_id };
    default:         return { val_str: state.val_str || null };
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

  const { data: posData, isLoading } = useQuery({
    queryKey: ['position-full', posId],
    queryFn: () => positionsApi.getFull(posId),
    enabled: !!posId,
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

  const updateMut = useMutation({
    mutationFn: ({ name }: { name: string }) => positionsApi.update(posId, { name }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['position-full', posId] }); qc.invalidateQueries({ queryKey: ['positions'] }); setEditingName(false); toast('Название сохранено', 'success'); },
    onError: () => toast('Ошибка', 'error'),
  });

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
      ? [...posParents].reverse().map((c: { name: string }) => c.name).join(' / ')
      : String(_catId);

  const setField = (paramId: number, update: Partial<FieldState>) => {
    setFieldStates(prev => ({ ...prev, [paramId]: { ...prev[paramId], ...update } }));
  };

  if (isLoading) return <div className="loading"><div className="spinner" /> Загрузка карточки...</div>;
  if (!posData) return <div className="empty-state" style={{ padding: 40 }}><p>Изделие не найдено</p></div>;

  const { position, position_parameters } = posData;

  return (
    <>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <button className="btn btn-ghost" onClick={() => navigate(-1)}>← Назад</button>
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
                    <input className="form-control" value={nameVal} onChange={e => setNameVal(e.target.value)}
                      onKeyDown={e => { if (e.key === 'Enter') updateMut.mutate({ name: nameVal }); if (e.key === 'Escape') setEditingName(false); }}
                      autoFocus />
                    <button className="btn btn-primary btn-xs" onClick={() => updateMut.mutate({ name: nameVal })}>✓</button>
                    <button className="btn btn-secondary btn-xs" onClick={() => setEditingName(false)}>✕</button>
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 18, fontWeight: 700 }}>{position.name}</span>
                    <button className="btn btn-ghost btn-icon btn-xs" title="Переименовать" onClick={() => setEditingName(true)}>✏</button>
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
              <p>У класса «{getCatName(position.category_id)}» нет параметров.<br />Добавьте их в разделе «Классификатор».</p>
            </div>
          )}

          {position_parameters.length > 0 && (
            <div style={{ padding: '8px 16px 16px' }}>
              {[...position_parameters].map(pv => {
                const typeCode = pv.parameter.paramType?.code ?? '';
                const state = fieldStates[pv.parameter.id] ?? initFieldState(pv);
                const unit = pv.parameter.unit;
                const isSaving = savingId === pv.parameter.id;

                return (
                  <div key={pv.parameter.id} style={{ padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16, flexWrap: 'wrap' }}>
                      <div style={{ width: 220, flexShrink: 0 }}>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>{pv.parameter.name}</div>
                        <div style={{ display: 'flex', gap: 6, marginTop: 4, alignItems: 'center' }}>
                          <span className={typeClass(typeCode)}>{TYPE_LABELS[typeCode] ?? typeCode}</span>
                          {unit && <span className="badge badge-gray">{unit.symbol}</span>}
                        </div>
                        <div className="text-muted" style={{ fontSize: 11, marginTop: 2 }}>{pv.parameter.short_name}</div>
                      </div>

                      <div style={{ flex: 1, minWidth: 180 }}>
                        {typeCode === 'real' && (
                          <input type="number" step="any" className="form-control"
                            value={state.val_real}
                            onChange={e => setField(pv.parameter.id, { val_real: e.target.value })}
                            placeholder="Введите число" />
                        )}
                        {typeCode === 'integer' && (
                          <input type="number" step="1" className="form-control"
                            value={state.val_int}
                            onChange={e => setField(pv.parameter.id, { val_int: e.target.value })}
                            placeholder="Введите целое число" />
                        )}
                        {typeCode === 'string' && (
                          <input type="text" className="form-control"
                            value={state.val_str}
                            onChange={e => setField(pv.parameter.id, { val_str: e.target.value })}
                            placeholder="Введите текст" />
                        )}
                        {typeCode === 'datetime' && (
                          <input type="datetime-local" className="form-control"
                            value={state.val_dt}
                            onChange={e => setField(pv.parameter.id, { val_dt: e.target.value })} />
                        )}
                        {typeCode === 'enum' && pv.parameter.enumType && (
                          <EnumSelect
                            enumTypeId={pv.parameter.enumType.id}
                            value={state.enum_val_id}
                            onChange={id => setField(pv.parameter.id, { enum_val_id: id })} />
                        )}
                        {!['real','integer','string','datetime','enum'].includes(typeCode) && (
                          <input type="text" className="form-control"
                            value={state.val_str}
                            onChange={e => setField(pv.parameter.id, { val_str: e.target.value })} />
                        )}
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 2 }}>
                        <button className="btn btn-secondary btn-xs" title="Сохранить"
                          disabled={isSaving} onClick={() => saveParam(pv)}>
                          {isSaving ? '...' : 'Сохранить'}
                        </button>
                        <button className="btn btn-ghost btn-xs" title="Очистить значение"
                          style={{ color: '#ef4444' }}
                          disabled={isSaving} onClick={() => deleteParam(pv)}>
                          Очистить
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
