import { NavLink, Outlet } from 'react-router-dom';

const NAV = [
  { to: '/classifier', icon: '🌳', label: 'Классификатор' },
  { to: '/enums',      icon: '📋', label: 'Перечисления' },
  { to: '/positions',  icon: '📦', label: 'Изделия' },
  { to: '/parameters', icon: '⚙️', label: 'Параметры' },
  { to: '/units',      icon: '📏', label: 'Единицы измерения' },
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
              <span className="icon">{n.icon}</span>
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
