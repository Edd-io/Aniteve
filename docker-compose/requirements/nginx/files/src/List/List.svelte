<script lang='ts'>
	import { onMount } from 'svelte';

	export let menu: any;

	const	serverUrl				= '';
	let		progressData: any		= [];
	let		buttonActive			= false;

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
				animeResumed.remove();
				menu.selected = 3;
			}, 400);
		}, 500);
	}

</script>

<main class='main'>
	<div class='title-div'>
		<h1>Liste de visionnage</h1>
	</div>
	<div class='list'>
		{#each progressData as animeData}
			<button class='anime-div' id={'anime' + animeData.anime.id} on:click={() => {
				hideAll('anime' + animeData.anime.id, animeData.anime);
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
		{/each}
	</div>
</main>

<style>
	main {
		flex: 1;
		height: 100%;
		color: white;
		padding: 1rem;
		overflow: scroll;
	}
	.list {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
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
</style>