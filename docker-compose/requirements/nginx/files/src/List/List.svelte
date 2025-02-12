<script lang='ts'>
	import { onMount } from 'svelte';
	import { navigate } from 'svelte-routing';
    import { on } from 'svelte/events';

	export let menu: any;

	const	serverUrl				= '';
	let		progressData: any		= [];
	let		buttonActive			= false;
	let		listMode				= true;

	onMount(() => {
		const interval = setInterval(() => {
			if (menu.user.id !== -1)
			{
				getDataProgress();
				clearInterval(interval);
			}
		}, 100);
	});

	menu.dominantColor = '#c7c7c75c';
	menu.selected = 2;

	function getDataProgress()
	{
		fetch(serverUrl + '/api/get_all_progress', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({idUser: menu.user.id}),
		})
		.then((response) => {
			return (response.json());
		})
		.then((json) => {
			progressData = json;
		})
		.catch((error) => {
			console.warn(error);
		});
	}

	function hideAll(id: string, data: any, event: any)
	{
		if (buttonActive)
			return;
		if (event.target.id === 'deleteBtn')
			return;
		buttonActive = true;
		const animeResumed = document.querySelector('#' + id) as HTMLElement;
		const copy = animeResumed.cloneNode(true) as HTMLElement;
		const pos = animeResumed.getBoundingClientRect();

		animeResumed.parentNode?.insertBefore(copy, animeResumed);
		copy.style.opacity = '0';
		animeResumed.remove();
		document.body.appendChild(animeResumed);

		animeResumed.style.position = 'absolute';
		animeResumed.style.top = `calc(${pos.top}px - 1rem)`;
		animeResumed.style.left = `calc(${pos.left}px - 0.1rem)`;
		animeResumed.style.width = pos.width + 'px';
		animeResumed.style.height = pos.height + 'px';
		animeResumed.style.zIndex = '999';
		const partClass = document.querySelector('.main');
		const htmlPartClass = partClass as HTMLElement;
		htmlPartClass.style.animation = 'fadeOut 0.5s';
		setTimeout(() => {
			htmlPartClass.style.opacity = '0';
		}, 450);
		setTimeout(() => {
			menu.data = data;
			animeResumed.style.animation = 'choose 0.5s';
			animeResumed.style.opacity = '0';
			setTimeout(() => {
				menu.data = data;
				menu.selected = 3;
				navigate('/anime', {replace: true});
			}, 400);
		}, 500);
	}

	function confirmDelete(animeId: string, id: number)
	{
		const	animeResumed = document.querySelector('#' + animeId) as HTMLElement;
		const	btnDelete = animeResumed.querySelector('#deleteBtn') as HTMLElement;

		if (btnDelete.innerText == 'Supprimer')
			btnDelete.innerText = 'Confirmer';
		else
		{
			fetch(serverUrl + '/api/delete_progress', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': localStorage.getItem('token') || '',
				},
				body: JSON.stringify({idUser: menu.user.id, id: id}),
			})
			.catch((error) => {
				console.warn(error);
			});
			animeResumed.remove();
		}
	}

</script>

<main class='main'>
	<div class='title-div'>
		<h1>Liste de visionnage</h1>
	</div>
	<div class={!listMode ? 'tile-div' : 'line-mode'}>
		<div class='filter-bar'>
			<button on:click={() => listMode = !listMode}>
				<p style="font-size: 0.8rem; color: white;">
					{#if listMode}
						Mode liste
					{:else}
						Mode tuile
					{/if}
				</p>
			</button>
		</div>
		{#each progressData as animeData}
				{#if !listMode}
					<button class='anime-div' id={'anime' + animeData.anime.id} on:click={(event) => {
						hideAll('anime' + animeData.anime.id, animeData.anime, event);
					}}>
							<div class='img-container'>
								<img src={animeData.poster} alt={animeData.title} />
								<div class='progress-bar' style='width: {animeData.progress}%'></div>
							</div>
							<h2>{animeData.anime.title.length > 30 ? animeData.anime.title.substring(0, 30) + '...' : animeData.anime.title}</h2>
							<div class='status'>
								{#if animeData.completed === 0 || animeData.completed === 2}
									<p style="background-color: #fc7b03;">En cours</p>
								{:else if animeData.completed === 1}
									<p style="background-color: #0da11e;">À jour</p>
								{:else if animeData.completed === 3}
									<p style="background-color: #2e8c8b;">Nouvelle saison</p>
								{/if}
							</div>
					</button>
				{:else}
					<button class='anime-div-line' id={'anime' + animeData.anime.id} on:click={(event) => {
						hideAll('anime' + animeData.anime.id, animeData.anime, event);
					}}>
						<img src={animeData.poster} alt={animeData.title} />
						<div>
							<p>{animeData.anime.title}</p>
							<p style='font-size: 0.8rem; color: #c7c7c7;'>
								{#if animeData.completed === 0 || animeData.completed === 2}
									En cours
								{:else if animeData.completed === 1}
									À jour
								{:else if animeData.completed === 3}
									Nouvelle saison
								{/if}
							</p>
						</div>
						<div class='btns'>
							<!-- svelte-ignore a11y_click_events_have_key_events -->
							<div on:click={() => {confirmDelete('anime' + animeData.anime.id, animeData.anime.id)}} role="button" tabindex="0" id='deleteBtn'>
								Supprimer
							</div>

						</div>
					</button>
				{/if}
		{/each}
	</div>
</main>

<style>
	main {
		flex: 1;
		height: 100%;
		color: white;
		padding: 1rem;
	}
	.tile-div {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
	}
	.line-mode {
		display: flex;
		flex-direction: column;
		align-items: center;
		overflow: auto;
		height: calc(100% - 3.5rem);
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
	.anime-div {
		position: relative;
		display: flex;
		flex-direction: column;
		margin-block: 1rem;
		margin-inline: 0.3rem;
		background-color: #c7c7c75c;
		border-radius: 0.5rem;
		padding: 0.5rem;
		width: 8rem;
		height: 15rem;
		min-width: 8rem;
		text-align: center;
		transition: background-color 0.5s, transform 0.5s;
		cursor: pointer;
		color: white;
		border: none;
	}
	.anime-div:hover {
		background-color: #c7c7c7af;
		transform: scale(1.05);
	}
	.anime-div .img-container {
		width: 100%;
		height: 11rem;
		margin-bottom: 0.5rem;
		border-radius: 0.5rem;
		position: relative;
		overflow: hidden;
	}
	.anime-div .img-container img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		border-radius: 0.5rem;
	}
	.anime-div h2{
		font-size: 0.8rem;
		text-align: center;
		width: 100%;
		height: 2rem;
	}
	.anime-div-line {
		width: 95%;
		height: 5rem;
		background-color: #c7c7c75c;
		border-radius: 0.5rem;
		padding: 0.5rem;
		margin-block: 0.5rem;
		text-align: left;
		transition: background-color 0.5s, transform 0.5s;
		cursor: pointer;
		color: white;
		border: none;
		display: flex;
		align-items: center;
	}
	.anime-div-line:hover {
		background-color: #c7c7c7af;
		transform: scale(1.02);
	}
	.anime-div-line img {
		width: 4.5rem;
		height: 4.5rem;
		min-width: 4.5rem;
		object-fit: cover;
		border-radius: 0.5rem;
		margin-right: 0.5rem;
	}
	.anime-div-line p {
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		font-size: 0.8rem;
	}
	.anime-div-line .btns {
		display: flex;
		flex-direction: column;
		align-items: end;
		margin-left: auto;
	}
	.anime-div-line .btns div {
		padding: 0.2rem 0.5rem;
		margin-block: 0.2rem;
		cursor: pointer;
		border-radius: 0.5rem;
		font-size: 0.8rem;
	}
	.anime-div-line .btns div:hover {
		background-color: #e94444af;
	}
	.status {
		position: absolute;
		bottom: 0;
		left: 0;
		width: 100%;
		height: 1rem;
		border-radius: 0 0 0.5rem 0.5rem;
	}
	.status p {
		font-size: 0.6rem;
		text-align: center;
		width: 100%;
		height: 100%;
		display: flex;
		justify-content: center;
		align-items: center;
		border-radius: 0 0 0.5rem 0.5rem;
	}
	.filter-bar {
		width: 95%;
		display: flex;
		justify-content: flex-end;
		background-color: #c7c7c75c;
		border-radius: 0.5rem;
		margin-block: 0.5rem;
	}
	.filter-bar button {
		background: none;
		border: none;
		border-radius: 0.5rem;
		padding: 0.2rem;
		padding-inline: 0.5rem;
		cursor: pointer;
		margin: 0.2rem;
		transition: background-color 0.2s;
	}
	.filter-bar button:hover {
		background-color: #c7c7c7af;
	}
</style>