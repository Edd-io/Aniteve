<script lang='ts'>
	import '@fortawesome/fontawesome-free/css/all.css';
	import { onMount } from 'svelte';
	import { navigate } from 'svelte-routing';

	export let menu: any;

	const serverUrl = '';
	let progressData: any = [];
	let buttonActive = false;
	let viewMode: 'grid' | 'list' = 'list';
	let isLoading = true;
	let filterStatus = 'all';

	menu.dominantColor = '#0d0d0d';
	menu.selected = 2;

	onMount(() => {
		const interval = setInterval(() => {
			if (menu.user.id !== -1) {
				getDataProgress();
				clearInterval(interval);
			}
		}, 100);
	});

	function getDataProgress() {
		fetch(serverUrl + '/api/get_all_progress', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({idUser: menu.user.id}),
		})
		.then(response => response.json())
		.then(json => {
			progressData = json;
			isLoading = false;
		})
		.catch(error => {
			console.warn(error);
			isLoading = false;
		});
	}

	function selectAnime(id: string, data: any, event: any) {
		if (buttonActive) return;
		if ((event.target as HTMLElement).closest('.delete-btn')) return;

		buttonActive = true;
		const element = document.getElementById(id);
		if (element) {
			element.style.animation = 'choose 0.4s ease-out';
			element.style.opacity = '0';
		}

		setTimeout(() => {
			menu.data = data;
			menu.selected = 4;
			navigate('/player', {replace: true});
		}, 350);
	}

	function confirmDelete(animeId: string, id: number) {
		const element = document.getElementById(animeId);
		const btn = element?.querySelector('.delete-btn') as HTMLElement;

		if (btn?.dataset.confirm !== 'true') {
			btn.dataset.confirm = 'true';
			btn.innerHTML = '<i class="fas fa-check"></i> Confirmer';
			setTimeout(() => {
				if (btn) {
					btn.dataset.confirm = 'false';
					btn.innerHTML = '<i class="fas fa-trash"></i>';
				}
			}, 3000);
		} else {
			fetch(serverUrl + '/api/delete_progress', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': localStorage.getItem('token') || '',
				},
				body: JSON.stringify({idUser: menu.user.id, id: id}),
			})
			.then(() => {
				if (element) {
					element.style.animation = 'fadeOut 0.3s ease-out';
					setTimeout(() => element.remove(), 280);
				}
			})
			.catch(console.warn);
		}
	}

	function getStatusInfo(status: number) {
		switch(status) {
			case 0:
			case 2:
				return { label: 'En cours', color: '#f59e0b', icon: 'fa-play' };
			case 1:
				return { label: 'Terminé', color: '#22c55e', icon: 'fa-check' };
			case 3:
				return { label: 'Nouvelle saison', color: '#3b82f6', icon: 'fa-star' };
			default:
				return { label: 'Inconnu', color: '#6b7280', icon: 'fa-question' };
		}
	}

	function getFilteredData() {
		if (filterStatus === 'all') return progressData;
		if (filterStatus === 'watching') return progressData.filter((d: any) => d.completed === 0 || d.completed === 2);
		if (filterStatus === 'completed') return progressData.filter((d: any) => d.completed === 1);
		if (filterStatus === 'new') return progressData.filter((d: any) => d.completed === 3);
		return progressData;
	}
</script>

<main>
	<div class="page-header">
		<h1>Ma Liste</h1>
		<div class="header-controls">
			<div class="filter-group">
				<button
					class="filter-btn"
					class:active={filterStatus === 'all'}
					on:click={() => filterStatus = 'all'}
				>
					Tout
				</button>
				<button
					class="filter-btn"
					class:active={filterStatus === 'watching'}
					on:click={() => filterStatus = 'watching'}
				>
					En cours
				</button>
				<button
					class="filter-btn"
					class:active={filterStatus === 'completed'}
					on:click={() => filterStatus = 'completed'}
				>
					Terminé
				</button>
				<button
					class="filter-btn"
					class:active={filterStatus === 'new'}
					on:click={() => filterStatus = 'new'}
				>
					Nouveau
				</button>
			</div>
			<div class="view-toggle">
				<button
					class:active={viewMode === 'list'}
					on:click={() => viewMode = 'list'}
				>
					<i class="fas fa-list"></i>
				</button>
				<button
					class:active={viewMode === 'grid'}
					on:click={() => viewMode = 'grid'}
				>
					<i class="fas fa-th"></i>
				</button>
			</div>
		</div>
	</div>

	{#if isLoading}
		<div class="loading">
			<i class="fas fa-spinner fa-spin"></i>
		</div>
	{:else if getFilteredData().length === 0}
		<div class="empty-state">
			<i class="fas fa-film"></i>
			<p>Aucun anime dans votre liste</p>
			<span>Regarde des anime pour les voir apparaître ici</span>
		</div>
	{:else}
		<div class="anime-container" class:grid-view={viewMode === 'grid'}>
			{#each getFilteredData() as item}
				{@const status = getStatusInfo(item.completed)}
				<div
					class="anime-item"
					class:grid-item={viewMode === 'grid'}
					id={'anime-' + item.anime.id}
					role="button"
					tabindex="0"
					on:click={(e) => selectAnime('anime-' + item.anime.id, item.anime, e)}
					on:keydown={(e) => e.key === 'Enter' && selectAnime('anime-' + item.anime.id, item.anime, e)}
				>
					<div class="poster">
						<img src={item.poster} alt={item.anime.title} />
						<div class="progress-bar">
							<div class="progress" style="width: {item.progress}%"></div>
						</div>
						{#if item.completed === 2}
							<span class="new-badge">Nouvel épisode</span>
						{/if}
					</div>

					<div class="info">
						<h3>{item.anime.title}</h3>
						<p class="episode-info">
							Épisode {item.episode} {item.season_name ? '• ' + item.season_name : ''}
						</p>
						<div class="status-badge" style="--status-color: {status.color}">
							<i class="fas {status.icon}"></i>
							{status.label}
						</div>
					</div>

					<button
						class="delete-btn"
						on:click|stopPropagation={() => confirmDelete('anime-' + item.anime.id, item.anime.id)}
					>
						<i class="fas fa-trash"></i>
					</button>
				</div>
			{/each}
		</div>
	{/if}
</main>

<style>
	main {
		flex: 1;
		height: 100%;
		color: white;
		padding: 1.5rem 2rem;
		overflow-y: auto;
		overflow-x: hidden;
	}

	.page-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1.5rem;
		flex-wrap: wrap;
		gap: 1rem;
	}

	.page-header h1 {
		font-size: 1.5rem;
		font-weight: 600;
		color: #ffffff;
	}

	.header-controls {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.filter-group {
		display: flex;
		gap: 0.5rem;
	}

	.filter-btn {
		padding: 0.5rem 1rem;
		background-color: rgba(255, 255, 255, 0.05);
		border: none;
		border-radius: 0.5rem;
		color: rgba(255, 255, 255, 0.6);
		font-size: 0.85rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.filter-btn:hover {
		background-color: rgba(255, 255, 255, 0.1);
		color: rgba(255, 255, 255, 0.8);
	}

	.filter-btn.active {
		background-color: rgba(245, 158, 11, 0.15);
		color: #f59e0b;
	}

	.view-toggle {
		display: flex;
		background-color: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
		padding: 0.25rem;
	}

	.view-toggle button {
		padding: 0.5rem 0.75rem;
		background: none;
		border: none;
		border-radius: 0.375rem;
		color: rgba(255, 255, 255, 0.5);
		cursor: pointer;
		transition: all 0.2s;
	}

	.view-toggle button:hover {
		color: rgba(255, 255, 255, 0.8);
	}

	.view-toggle button.active {
		background-color: rgba(255, 255, 255, 0.1);
		color: #ffffff;
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 50vh;
		font-size: 2rem;
		color: rgba(255, 255, 255, 0.5);
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 50vh;
		color: rgba(255, 255, 255, 0.5);
		gap: 1rem;
	}

	.empty-state i {
		font-size: 4rem;
		opacity: 0.3;
	}

	.empty-state p {
		font-size: 1.1rem;
		color: rgba(255, 255, 255, 0.7);
	}

	.empty-state span {
		font-size: 0.9rem;
		color: rgba(255, 255, 255, 0.4);
	}

	.empty-state button {
		margin-top: 0.5rem;
		padding: 0.75rem 1.5rem;
		background-color: #f59e0b;
		border: none;
		border-radius: 0.5rem;
		color: #000;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.empty-state button:hover {
		background-color: #fbbf24;
	}

	.anime-container {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.anime-container.grid-view {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
		gap: 1rem;
	}

	.anime-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 0.75rem;
		background-color: rgba(255, 255, 255, 0.03);
		border: 1px solid rgba(255, 255, 255, 0.05);
		border-radius: 0.75rem;
		cursor: pointer;
		transition: all 0.2s;
		text-align: left;
		color: #fff;
	}

	.anime-item:hover {
		background-color: rgba(255, 255, 255, 0.06);
		border-color: rgba(255, 255, 255, 0.1);
	}

	.anime-item.grid-item {
		flex-direction: column;
		padding: 0;
		background: none;
		border: none;
	}

	.anime-item.grid-item:hover {
		transform: scale(1.03);
		background: none;
	}

	.poster {
		position: relative;
		flex-shrink: 0;
		width: 70px;
		height: 100px;
		border-radius: 0.5rem;
		overflow: hidden;
	}

	.grid-item .poster {
		width: 100%;
		height: auto;
		aspect-ratio: 2 / 3;
	}

	.poster img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.progress-bar {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 3px;
		background-color: rgba(0, 0, 0, 0.5);
	}

	.progress {
		height: 100%;
		background-color: #f59e0b;
		transition: width 0.3s;
	}

	.new-badge {
		position: absolute;
		top: 0.5rem;
		left: 0.5rem;
		background-color: #f59e0b;
		color: #000;
		font-size: 0.6rem;
		font-weight: 600;
		padding: 0.15rem 0.4rem;
		border-radius: 0.25rem;
	}

	.info {
		flex: 1;
		min-width: 0;
	}

	.grid-item .info {
		padding: 0.75rem;
		width: 100%;
	}

	.info h3 {
		font-size: 0.95rem;
		font-weight: 500;
		margin-bottom: 0.25rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.grid-item .info h3 {
		font-size: 0.85rem;
	}

	.episode-info {
		font-size: 0.8rem;
		color: rgba(255, 255, 255, 0.5);
		margin-bottom: 0.5rem;
	}

	.status-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.75rem;
		padding: 0.25rem 0.6rem;
		background-color: rgba(var(--status-color), 0.15);
		color: var(--status-color);
		border-radius: 1rem;
	}

	.status-badge i {
		font-size: 0.65rem;
	}

	.delete-btn {
		padding: 0.75rem;
		background-color: rgba(255, 255, 255, 0.05);
		border: none;
		border-radius: 0.5rem;
		color: rgba(255, 255, 255, 0.4);
		cursor: pointer;
		transition: all 0.2s;
		flex-shrink: 0;
	}

	.delete-btn:hover {
		background-color: rgba(239, 68, 68, 0.2);
		color: #ef4444;
	}

	.grid-item .delete-btn {
		position: absolute;
		top: 0.5rem;
		right: 0.5rem;
		padding: 0.5rem;
		background-color: rgba(0, 0, 0, 0.7);
		opacity: 0;
	}

	.grid-item:hover .delete-btn {
		opacity: 1;
	}

	@media (max-width: 768px) {
		.page-header {
			flex-direction: column;
			align-items: flex-start;
		}

		.header-controls {
			width: 100%;
			flex-direction: column;
			align-items: stretch;
		}

		.filter-group {
			flex-wrap: wrap;
		}
	}
</style>
