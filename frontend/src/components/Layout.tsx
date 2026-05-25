import { NavLink, Outlet } from 'react-router-dom';

const NAV = [
	{ to: '/classifier', label: 'Классификатор' },
	{ to: '/enums', label: 'Перечисления' },
	{ to: '/positions', label: 'Изделия' },
	{ to: '/parameters', label: 'Параметры' },
	{ to: '/units', label: 'Единицы' },
	{ to: '/stats', label: 'Статистика' },
	{ to: '/settings', label: 'Настройки' },
];

export function Layout() {
	return (
		<div className="app-shell">
			<header className="topbar">
				<div className="topbar-logo">Справочник</div>
				<nav>
					{NAV.map((n) => (
						<NavLink
							key={n.to}
							to={n.to}
							className={({ isActive }) => `topbar-item${isActive ? ' active' : ''}`}
						>
							{n.label}
						</NavLink>
					))}
				</nav>
			</header>
			<main className="main-content">
				<Outlet />
			</main>
		</div>
	);
}
