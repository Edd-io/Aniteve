<script lang='ts'>
	import { onMount } from 'svelte';

	export let menu: any;

	const	serverUrl				= '';
	let		downloads: any[]		= [];

	menu.dominantColor = '#c7c7c75c';
	menu.selected = 6;

	onMount(() => {
		getDownloads();
		const interval = setInterval(() => {
			getDownloads();
		}, 1500);
		return () => clearInterval(interval);
	});

	function getDownloads()
	{
		fetch(serverUrl + '/api/get_status_download', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
		})
		.then(response => response.json())
		.then(data => {downloads = data})
		.catch((error) => {
			console.warn('Error:', error);
		});
	}

	function delDownload(id: number)
	{
		fetch(serverUrl + '/api/del_download', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({ id: id }),
		})
		.then(response => response.json())
		.then(data => {
			getDownloads();
		})
		.catch((error) => {
			console.warn('Error:', error);
		});
	}

	function downloadEpisode(name: string)
	{
		const url = serverUrl + '/api/download/' + name;
		window.open(url, '_blank');
	}
</script>

<main>
	<div class='title-div'>
		<h1>Téléchargement</h1>
	</div>
	<div class='list-downaloads'>
		{#each downloads as download}
			<div class='download'>
				<img src={download.poster} alt='anime'>
				<div class='download-info'>
					<p>{download.name}</p>
					{#if download.waiting}
						<p class='info'>Status : En attente</p>
					{:else if download.failed || download.finished}
						<p class='info'>Status : {download.failed ? 'Échec' : 'Terminé'}</p>
					{:else}
						{#if download.progress == -1}
							<p class='info'>Progression : En cours (Aucune donnée de progression)</p>
						{:else}
							<p class='info'>Progression : {download.progress}%</p>
						{/if}
					{/if}
				</div>
				<div class='download-buttons'>
					{#if download.finished}
						<button on:click={() => {
							downloadEpisode(download.name);
						}}>Télécharger</button>
						<button on:click={() => {
							delDownload(download.id);
						}}>Supprimer</button>
					{:else if download.failed}
						<button on:click={() => {
							delDownload(download.id);
						}}>Supprimer</button>
					{/if}
				</div>
			</div>
		{/each}
</main>

<style>
	main {
		flex: 1;
		height: 100%;
		color: white;
		padding: 1rem;
		overflow: auto;
	}
	.title-div {
		padding-inline: 1rem;
		padding-block: 0.3rem;
		background-color: #c7c7c75c;
		border-radius: 0.5rem;
		display: flex;
		align-items: center;
	}
	.title-div h1 {
		font-size: 1rem;
		text-align: center;
		width: 100%;
		margin-block: 0.5rem;
	}
	.list-downaloads {
		display: flex;
		flex-direction: column;
	}
	.download {
		display: flex;
		background-color: #c7c7c75c;
		border-radius: 0.5rem;
		padding-inline: 1rem;
		padding-block: 0.5rem;
		margin-block: 0.5rem;
		height: 8rem;
		align-items: center;
	}
	.download img {
		height: 100%;
		width: 5rem;
		border-radius: 0.5rem;
		object-fit: cover;
		margin-right: 1rem;
	}
	.download-info {
		display: flex;
		flex-direction: column;
	}
	.download-info .info {
		font-size: 0.8rem;
		color: #c7c7c7;
		margin-top: 0.5rem;
	}
	.download-buttons {
		display: flex;
		flex-direction: column;
		margin-left: auto;
		height: 100%;
		padding-block: 1rem;
		justify-content: center;
	}
	.download-buttons button {
		background-color: #c7c7c7;
		border: none;
		border-radius: 0.5rem;
		padding-inline: 0.5rem;
		padding-block: 0.2rem;
		font-size: 0.8rem;
		cursor: pointer;
		margin-block: 0.3rem;
		width: 6rem;
	}
	.download-buttons button:hover {
		background-color: #c7c7c75c;
	}
</style>