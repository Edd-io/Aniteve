<script lang="ts">
	import '@fortawesome/fontawesome-free/css/all.css';
	import { onMount } from 'svelte';
	import { navigate } from 'svelte-routing';

	export let menu: any;

	const	serverUrl				= '';
	let		progressData: any		= [];
	let		nbAnimeResume			= 0;
	let		nbAnimeSeason			= 0;
	let		buttonActive			= false;

	menu.dominantColor = '#c7c7c75c';
	menu.selected = 0;
	onMount(() => {
		const interval = setInterval(() => {
			if (menu.user.id !== -1)
			{
				getDataProgress();
				clearInterval(interval);
			}
		}, 100);
	});

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
			if (!progressData.filter)
				return;
			nbAnimeResume = progressData.filter((animeData: any) => animeData.completed === 0 || animeData.completed === 2).length;
			nbAnimeSeason = progressData.filter((animeData: any) => animeData.completed === 3).length;
		})
		.catch((error) => {
			console.warn(error);
		});
	}

	function hideAll(id: string, data: any)
	{
		if (buttonActive)
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
		const partClasses = document.querySelectorAll('.part');
		partClasses.forEach(partClass => {
			const htmlPartClass = partClass as HTMLElement;
			htmlPartClass.style.animation = 'fadeOut 0.5s';
			setTimeout(() => {
				htmlPartClass.style.opacity = '0';
			}, 450);
		});
		setTimeout(() => {
			menu.data = data;
			animeResumed.style.animation = 'choose 0.5s';
			animeResumed.style.opacity = '0';
			setTimeout(() => {
				animeResumed.remove();
				menu.selected = 3;
				navigate('/anime', {replace: true});
			}, 400);
		}, 500);
	}

</script>

<main>
	<h2 style="text-align: right; width: 100%; margin-bottom: 1rem">Bonjour {menu.user.name} !</h2>
	{#if nbAnimeResume > 0}
		<div class='part'>
			<div class='title-div'>
				<h1>Reprendre / Nouveaux épisodes</h1>
				<div style="margin-left: auto; display: flex;">
					<button class='arrow-div arrow-left' aria-label="Previous" on:click={() => {
						document.querySelector('#list-anime-div-resume').scrollBy(-100, 0);
					}}>
						<i class='fas fa-arrow-left'></i>
					</button>
					<button class='arrow-div arrow-right' aria-label="Next" style="margin-left: 0.5rem;" on:click={() => {
						document.querySelector('#list-anime-div-resume').scrollBy(100, 0);
					}}>
						<i class='fas fa-arrow-right'></i>
					</button>
				</div>
			</div>
			<div class='list-anime-div' id='list-anime-div-resume'>
				{#if progressData.length > 0}
					{#each progressData as animeData}
						{#if (animeData.completed === 0 || animeData.completed === 2)}
							<button class='anime-div' id={'anime' + animeData.anime.id} on:click={() => {
								hideAll('anime' + animeData.anime.id, animeData.anime);
							}}>
								<div class='img-container'>
									<img src={animeData.poster} alt={animeData.title} />
									<div class='progress-bar' style='width: {animeData.progress}%'></div>
									{#if animeData.completed === 2}
										<div class='new-episode'>Nouvel épisode</div>
									{/if}
								</div>
								<h2>{animeData.anime.title.length > 30 ? animeData.anime.title.substring(0, 30) + '...' : animeData.anime.title}</h2>
								<p>Episode {animeData.episode} {animeData.season_name ? animeData.season_name : animeData.season.split('/')[0]}</p>
							</button>
						{/if}
					{/each}
				{/if}
			</div>
		</div>
	{/if}
	{#if nbAnimeSeason > 0}
		<div class='part'>
			<div class='title-div'>
				<h1 class='title'>Nouvelles saisons</h1>
				<div style="margin-left: auto; display: flex;">
					<button class='arrow-div arrow-left' aria-label="Previous" on:click={() => {
						document.querySelector('#list-anime-div-season').scrollBy(-100, 0);
					}}>
						<i class='fas fa-arrow-left'></i>
					</button>
					<button class='arrow-div arrow-right' aria-label="Next" style="margin-left: 0.5rem;" on:click={() => {
						document.querySelector('#list-anime-div-season').scrollBy(100, 0);
					}}>
						<i class='fas fa-arrow-right'></i>
					</button>
				</div>
			</div>
			<div class='list-anime-div' id='list-anime-div-season'>
					{#if progressData.length > 0}
						{#each progressData as animeData}
							{#if animeData.completed === 3}
								<button class='anime-div' id={'anime' + animeData.anime.id} on:click={() => {
									hideAll('anime' + animeData.anime.id, animeData.anime);
								}}>
									<div class='img-container'>
										<img src={animeData.poster} alt={animeData.title} />
										<div class='progress-bar' style='width: {animeData.progress}%'></div>
									</div>
									<h2>{animeData.anime.title.length > 30 ? animeData.anime.title.substring(0, 30) + '...' : animeData.anime.title}</h2>
									<p>Episode {animeData.episode} {animeData.season_name ? animeData.season_name : animeData.season.split('/')[0]}</p>
								</button>
							{/if}
						{/each}
					{/if}
			</div>
		</div>
	{/if}
</main>

<style>
	main {
		flex: 1;
		height: 100%;
		color: white;
		padding: 1rem;
		overflow: auto;
	}
	.part {
		display: flex;
		flex-direction: column;
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
		font-size: 0.8rem;
	}
	.list-anime-div {
		display: flex;
		overflow-x: auto;
		flex-direction: row;
		width: 100%;
		scroll-behavior: smooth;
	}
	.list-anime-div::-webkit-scrollbar {
		display: none;
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
	.anime-div .progress-bar {
		background-color: #394ae6;
		height: 0.5rem;
		position: absolute;
		bottom: 0;
		left: 0;
		box-shadow: 0 0 5px #000000bb;
	}
	.anime-div h2{
		font-size: 0.8rem;
		text-align: center;
		width: 100%;
	} 
	.anime-div p {
		width: 100%;
		font-size: 0.6rem;
		position: absolute;
		bottom: 0.2rem;
		left: 50%;
		transform: translateX(-50%);
		color: #ccc;
	} 
	.arrow-div {
		cursor: pointer;
		background-color: #c7c7c7;
		border-radius: 0.3rem;
		border: none;
		font-size: 1.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 1.3rem;
		height: 1.3rem;
		z-index: 5;
		transition: background-color 0.3s;
	}
	.arrow-div:hover {
		background-color: #c7c7c7af;
	}
	.new-episode {
		position: absolute;
		top: 0;
		left: 0;
		background-color: #3244e9;
		color: white;
		padding: 0.2rem;
		border-end-end-radius: 0.5rem;
		font-size: 0.6rem;
	}
</style>