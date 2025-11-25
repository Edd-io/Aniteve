<script lang='ts'>
	import '@fortawesome/fontawesome-free/css/all.css';
	import { onMount } from 'svelte';

	export let menu: any;

	const serverUrl = '';
	let downloads: any[] = [];
	let isLoading = true;

	menu.dominantColor = '#0d0d0d';
	menu.selected = 6;

	onMount(() => {
		getDownloads();
		const interval = setInterval(getDownloads, 1500);
		return () => clearInterval(interval);
	});

	function getDownloads() {
		fetch(serverUrl + '/api/get_status_download', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
		})
		.then(response => response.json())
		.then(data => {
			downloads = data;
			isLoading = false;
		})
		.catch(error => {
			console.warn('Error:', error);
			isLoading = false;
		});
	}

	function delDownload(id: number) {
		fetch(serverUrl + '/api/del_download', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({ id }),
		})
		.then(() => getDownloads())
		.catch(console.warn);
	}

	function downloadEpisode(name: string) {
		window.open(serverUrl + '/api/download/' + name, '_blank');
	}

	function getStatusInfo(download: any) {
		if (download.waiting) {
			return { label: 'En attente', icon: 'fa-clock', color: '#6b7280' };
		}
		if (download.failed) {
			return { label: 'Échec', icon: 'fa-exclamation-circle', color: '#ef4444' };
		}
		if (download.finished) {
			return { label: 'Terminé', icon: 'fa-check-circle', color: '#22c55e' };
		}
		return { label: 'En cours', icon: 'fa-spinner fa-spin', color: '#f59e0b' };
	}
</script>

<main>
	<div class="page-header">
		<h1>Téléchargements</h1>
		<span class="download-count">{downloads.length} fichier{downloads.length !== 1 ? 's' : ''}</span>
	</div>

	{#if isLoading}
		<div class="loading">
			<i class="fas fa-spinner fa-spin"></i>
		</div>
	{:else if downloads.length === 0}
		<div class="empty-state">
			<i class="fas fa-download"></i>
			<p>Aucun téléchargement</p>
			<span>Les téléchargements apparaîtront ici</span>
		</div>
	{:else}
		<div class="downloads-list">
			{#each downloads as download}
				{@const status = getStatusInfo(download)}
				<div class="download-item">
					<div class="poster">
						<img src={download.poster} alt={download.name} />
					</div>

					<div class="info">
						<h3>{download.name}</h3>
						<div class="status" style="--status-color: {status.color}">
							<i class="fas {status.icon}"></i>
							<span>{status.label}</span>
						</div>
						{#if !download.waiting && !download.failed && !download.finished}
							<div class="progress-container">
								{#if download.progress === -1}
									<div class="progress-bar indeterminate">
										<div class="progress-fill"></div>
									</div>
									<span class="progress-text">Téléchargement...</span>
								{:else}
									<div class="progress-bar">
										<div class="progress-fill" style="width: {download.progress}%"></div>
									</div>
									<span class="progress-text">{download.progress}%</span>
								{/if}
							</div>
						{/if}
					</div>

					<div class="actions">
						{#if download.finished}
							<button class="btn-primary" on:click={() => downloadEpisode(download.name)}>
								<i class="fas fa-download"></i>
								Télécharger
							</button>
						{/if}
						{#if download.finished || download.failed}
							<button class="btn-danger" on:click={() => delDownload(download.id)}>
								<i class="fas fa-trash"></i>
							</button>
						{/if}
					</div>
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
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.page-header h1 {
		font-size: 1.5rem;
		font-weight: 600;
		color: #ffffff;
	}

	.download-count {
		font-size: 0.85rem;
		color: rgba(255, 255, 255, 0.5);
		padding: 0.25rem 0.75rem;
		background-color: rgba(255, 255, 255, 0.05);
		border-radius: 1rem;
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
		gap: 0.75rem;
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
	}

	.downloads-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.download-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background-color: rgba(255, 255, 255, 0.03);
		border: 1px solid rgba(255, 255, 255, 0.05);
		border-radius: 0.75rem;
		transition: all 0.2s;
	}

	.download-item:hover {
		background-color: rgba(255, 255, 255, 0.05);
		border-color: rgba(255, 255, 255, 0.08);
	}

	.poster {
		flex-shrink: 0;
		width: 60px;
		height: 85px;
		border-radius: 0.5rem;
		overflow: hidden;
	}

	.poster img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.info {
		flex: 1;
		min-width: 0;
	}

	.info h3 {
		font-size: 0.95rem;
		font-weight: 500;
		margin-bottom: 0.5rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.status {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		font-size: 0.8rem;
		color: var(--status-color);
		margin-bottom: 0.5rem;
	}

	.status i {
		font-size: 0.75rem;
	}

	.progress-container {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.progress-bar {
		flex: 1;
		height: 4px;
		background-color: rgba(255, 255, 255, 0.1);
		border-radius: 2px;
		overflow: hidden;
		max-width: 200px;
	}

	.progress-fill {
		height: 100%;
		background-color: #f59e0b;
		border-radius: 2px;
		transition: width 0.3s ease;
	}

	.progress-bar.indeterminate .progress-fill {
		width: 30%;
		animation: indeterminate 1.5s ease-in-out infinite;
	}

	@keyframes indeterminate {
		0% {
			transform: translateX(-100%);
		}
		100% {
			transform: translateX(400%);
		}
	}

	.progress-text {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.5);
		min-width: 80px;
	}

	.actions {
		display: flex;
		gap: 0.5rem;
		flex-shrink: 0;
	}

	.btn-primary {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.6rem 1rem;
		background-color: #f59e0b;
		border: none;
		border-radius: 0.5rem;
		color: #000;
		font-size: 0.85rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-primary:hover {
		background-color: #fbbf24;
	}

	.btn-danger {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0.6rem 0.75rem;
		background-color: rgba(239, 68, 68, 0.1);
		border: none;
		border-radius: 0.5rem;
		color: #ef4444;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-danger:hover {
		background-color: rgba(239, 68, 68, 0.2);
	}

	@media (max-width: 600px) {
		.download-item {
			flex-direction: column;
			align-items: flex-start;
		}

		.poster {
			width: 100%;
			height: auto;
			aspect-ratio: 16 / 9;
		}

		.actions {
			width: 100%;
			justify-content: flex-end;
		}

		.progress-bar {
			max-width: none;
		}
	}
</style>
