import { NavLink, Outlet } from 'react-router-dom';

const NAV = [
  { to: '/classifier', label: 'Классификатор' },
  { to: '/enums',      label: 'Перечисления' },
  { to: '/positions',  label: 'Изделия' },
  { to: '/parameters', label: 'Параметры' },
  { to: '/units',      label: 'Единицы измерения' },
  { to: '/stats',      label: 'Статистика' },
  { to: '/settings',   label: 'Настройки' },
];

export function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-logo">
          Справочник изделий
          <small>Управление классификатором</small>
        </div>
        <nav>
          {NAV.map(n => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) => `sidebar-item${isActive ? ' active' : ''}`}
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
