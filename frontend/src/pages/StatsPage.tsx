import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { statsApi, type IntegrityIssue } from '../api/stats';
import { enumsApi } from '../api/enums';

const ISSUE_LABELS: Record<string, string> = {
  self_reference:    'Категория — родитель самой себя',
  missing_parent:    'Отсутствует родительская категория',
  missing_category:  'Изделие ссылается на несуществующий класс',
};

export default function StatsPage() {
  const [integrityRun, setIntegrityRun] = useState(false);

  const { data: summary, isLoading: sLoading, refetch: rSum } =
    useQuery({ queryKey: ['stats-summary'],      queryFn: statsApi.getSummary });
  const { data: byCategory = [], isLoading: bLoading, refetch: rCat } =
    useQuery({ queryKey: ['stats-by-category'],  queryFn: statsApi.getByCategory });
  const { data: integrity,  isLoading: iLoading, refetch: rInt } =
    useQuery({ queryKey: ['stats-integrity'],    queryFn: statsApi.getIntegrity, enabled: integrityRun });
  // GET /enum/values — total enum values count
  const { data: allEnumValues = [], refetch: rEnums } =
    useQuery({ queryKey: ['enum-values-all'],    queryFn: enumsApi.getValues });

  const refresh = () => { rSum(); rCat(); rEnums(); if (integrityRun) rInt(); };

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Статистика</div>
          <div className="page-subtitle">Сводка по базе данных</div>
        </div>
        <button className="btn btn-secondary" onClick={refresh}>↺ Обновить</button>
      </div>

      <div className="page-body" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

        {/* ── Summary cards ── */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
          {[
            { label: 'Классов всего',        value: summary?.categories_total,  icon: '🌳', loading: sLoading },
            { label: 'Корневых классов',      value: summary?.categories_root,   icon: '📁', loading: sLoading },
            { label: 'Изделий всего',         value: summary?.positions_total,   icon: '📦', loading: sLoading },
            { label: 'Значений перечислений', value: allEnumValues.length,       icon: '📋', loading: false },
          ].map(stat => (
            <div key={stat.label} className="card" style={{ textAlign: 'center', padding: '20px 16px' }}>
              <div style={{ fontSize: 28, marginBottom: 6 }}>{stat.icon}</div>
              {stat.loading ? (
                <div className="spinner" style={{ margin: '0 auto' }} />
              ) : (
                <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent)' }}>
                  {stat.value ?? '—'}
                </div>
              )}
              <div className="text-muted" style={{ fontSize: 12, marginTop: 4 }}>{stat.label}</div>
            </div>
          ))}
        </div>

        {/* ── By-category table ── */}
        <div className="card">
          <div className="card-header">
            Статистика по классам
            <span className="badge badge-gray">{byCategory.length}</span>
          </div>
          {bLoading && <div className="loading"><div className="spinner" /> Загрузка...</div>}
          {!bLoading && byCategory.length === 0 && (
            <div className="empty-state"><p>Нет данных</p></div>
          )}
          {byCategory.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Класс</th>
                    <th style={{ textAlign: 'right' }}>Дочерних классов</th>
                    <th style={{ textAlign: 'right' }}>Изделий</th>
                  </tr>
                </thead>
                <tbody>
                  {[...byCategory]
                    .sort((a, b) => b.positions_count - a.positions_count)
                    .map(row => (
                      <tr key={row.id}>
                        <td className="text-muted font-mono">{row.id}</td>
                        <td style={{ fontWeight: 500 }}>{row.name}</td>
                        <td style={{ textAlign: 'right' }}>
                          {row.children_count > 0
                            ? <span className="badge badge-blue">{row.children_count}</span>
                            : <span className="text-muted">0</span>}
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          {row.positions_count > 0
                            ? <span className="badge badge-green">{row.positions_count}</span>
                            : <span className="text-muted">0</span>}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* ── Integrity check ── */}
        <div className="card">
          <div className="card-header">
            Проверка целостности
            {integrity && (
              <span className={`badge ${integrity.ok ? 'badge-green' : 'badge-orange'}`}>
                {integrity.ok ? '✓ OK' : `⚠ ${integrity.issues.length} проблем`}
              </span>
            )}
          </div>
          <div className="card-body">
            {!integrityRun ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <p className="text-muted">Нажмите «Проверить», чтобы запустить анализ целостности данных.</p>
                <button className="btn btn-secondary" onClick={() => setIntegrityRun(true)}>
                  🔎 Проверить
                </button>
              </div>
            ) : iLoading ? (
              <div className="loading"><div className="spinner" /> Проверка...</div>
            ) : !integrity ? (
              <p className="text-danger">Ошибка запроса</p>
            ) : integrity.ok ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--success)', fontWeight: 500 }}>
                <span style={{ fontSize: 20 }}>✓</span>
                Проблем не обнаружено. База данных целостна.
              </div>
            ) : (
              <div>
                <p className="text-muted" style={{ marginBottom: 12 }}>Обнаружены следующие проблемы:</p>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr><th>Тип проблемы</th><th>Класс (ID)</th><th>Изделие (ID)</th><th>Родитель (ID)</th></tr>
                    </thead>
                    <tbody>
                      {integrity.issues.map((issue: IntegrityIssue, i) => (
                        <tr key={i}>
                          <td>
                            <span className="badge badge-orange">
                              {ISSUE_LABELS[issue.type] ?? issue.type}
                            </span>
                          </td>
                          <td className="font-mono">{issue.category_id ?? '—'}</td>
                          <td className="font-mono">{issue.position_id ?? '—'}</td>
                          <td className="font-mono">{issue.parent_id   ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </>
  );
}
