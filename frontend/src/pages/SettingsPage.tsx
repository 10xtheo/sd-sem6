import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '../api/settings';
import { useToast } from '../components/Toast';
import { Modal } from '../components/Modal';

export default function SettingsPage() {
	const qc = useQueryClient();
	const { toast } = useToast();

	const [seedConfirm, setSeedConfirm] = useState(false);
	const [clearConfirm, setClearConfirm] = useState(false);
	const [clearInput, setClearInput] = useState('');

	// Роль: 'user' или 'admin'
	const [role, setRole] = useState<'user' | 'admin'>(() => {
		return (localStorage.getItem('app_role') as 'user' | 'admin') || 'user';
	});

	const handleRoleChange = (newRole: 'user' | 'admin') => {
		setRole(newRole);
		localStorage.setItem('app_role', newRole);
		toast(`Роль изменена на ${newRole === 'admin' ? 'Администратора' : 'Пользователя'}`, 'success');
	};

	const invalidateAll = () => {
		qc.invalidateQueries(); // clear every cached query after DB changes
	};

	const seedMut = useMutation({
		mutationFn: settingsApi.seed,
		onSuccess: (data) => {
			invalidateAll();
			setSeedConfirm(false);
			toast(data.detail ?? 'Тестовые данные загружены', 'success');
		},
		onError: (e: any) => toast(e?.response?.data?.detail ?? 'Ошибка', 'error'),
	});

	const clearMut = useMutation({
		mutationFn: settingsApi.clear,
		onSuccess: (data) => {
			invalidateAll();
			setClearConfirm(false);
			setClearInput('');
			toast(data.detail ?? 'База очищена', 'success');
		},
		onError: (e: any) => toast(e?.response?.data?.detail ?? 'Ошибка', 'error'),
	});

	return (
		<>
			<div className="page-header">
				<div>
					<div className="page-title">Настройки</div>
				</div>
			</div>

			<div className="page-body" style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 600 }}>
				{/* Role Selector */}
				<div className="card">
					<div className="card-header">Режим доступа</div>
					<div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
						<p>Выберите роль для просмотра интерфейса</p>
						<div style={{ display: 'flex', gap: 16 }}>
							<label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
								<input
									type="radio"
									name="role"
									value="user"
									checked={role === 'user'}
									onChange={() => handleRoleChange('user')}
								/>
								<span>Пользователь</span>
							</label>
							<label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
								<input
									type="radio"
									name="role"
									value="admin"
									checked={role === 'admin'}
									onChange={() => handleRoleChange('admin')}
								/>
								<span>Администратор</span>
							</label>
						</div>
						<p className="text-muted" style={{ fontSize: 12, marginTop: 4 }}>
							Текущая роль: <strong>{role === 'admin' ? 'Администратор' : 'Пользователь'}</strong>
						</p>
					</div>
				</div>

				{/* Seed */}
				<div className="card">
					<div className="card-header">Загрузить тестовые данные</div>
					<div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
						<p>
							Заполняет базу данных тестовыми классами, параметрами и изделиями из файла
							<span className="font-mono" style={{ marginLeft: 4 }}>
								data/test_data.json
							</span>
							.
						</p>
						<p className="text-muted" style={{ fontSize: 12 }}>
							Операция идемпотентна — повторный запуск не создаст дубликаты.
						</p>
						<div>
							<button
								className="btn btn-primary"
								onClick={() => setSeedConfirm(true)}
								disabled={seedMut.isPending}
							>
								{seedMut.isPending ? 'Загрузка...' : 'Заполнить тестовыми данными'}
							</button>
						</div>
					</div>
				</div>

				{/* Clear */}
				<div className="card" style={{ borderColor: '#fecaca' }}>
					<div className="card-header" style={{ color: 'var(--danger)' }}>
						Очистить базу данных
					</div>
					<div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
						<p>
							Безвозвратно удаляет <strong>все</strong> классы, параметры, изделия и перечисления.
						</p>
						<p className="text-muted" style={{ fontSize: 12 }}>
							Это действие нельзя отменить.
						</p>
						<div>
							<button
								className="btn btn-danger"
								onClick={() => setClearConfirm(true)}
								disabled={clearMut.isPending}
							>
								{clearMut.isPending ? 'Очистка...' : 'Очистить базу'}
							</button>
						</div>
					</div>
				</div>
			</div>

			{/* Seed confirm */}
			<Modal
				open={seedConfirm}
				onClose={() => setSeedConfirm(false)}
				title="Загрузить тестовые данные?"
				footer={
					<>
						<button className="btn btn-secondary" onClick={() => setSeedConfirm(false)}>
							Отмена
						</button>
						<button
							className="btn btn-primary"
							disabled={seedMut.isPending}
							onClick={() => seedMut.mutate()}
						>
							Загрузить
						</button>
					</>
				}
			>
				<p>
					Будут добавлены тестовые классы, параметры и изделия из файла{' '}
					<span className="font-mono">test_data.json</span>.
				</p>
				<p className="text-muted" style={{ marginTop: 6, fontSize: 12 }}>
					Существующие данные не удаляются.
				</p>
			</Modal>

			{/* Clear confirm */}
			<Modal
				open={clearConfirm}
				onClose={() => {
					setClearConfirm(false);
					setClearInput('');
				}}
				title="Очистить всю базу?"
				footer={
					<>
						<button
							className="btn btn-secondary"
							onClick={() => {
								setClearConfirm(false);
								setClearInput('');
							}}
						>
							Отмена
						</button>
						<button
							className="btn btn-danger"
							disabled={clearInput !== 'УДАЛИТЬ' || clearMut.isPending}
							onClick={() => clearMut.mutate()}
						>
							Удалить всё
						</button>
					</>
				}
			>
				<p>
					Это безвозвратно удалит <strong>все данные</strong>. Для подтверждения введите слово:
				</p>
				<div className="form-group" style={{ marginTop: 10 }}>
					<code style={{ display: 'block', padding: '4px 8px', background: '#f8fafc', marginBottom: 8 }}>
						УДАЛИТЬ
					</code>
					<input
						className="form-control"
						value={clearInput}
						onChange={(e) => setClearInput(e.target.value)}
						placeholder="Введите УДАЛИТЬ для подтверждения"
						autoFocus
					/>
				</div>
			</Modal>
		</>
	);
}
