<script lang='ts'>
    import { writable } from "svelte/store";
	import VideoOverlay from "./VideoOverlay.svelte";
	export let menu: any;

	const	serverUrl				= '';
	const	data					= menu.data;
	const	genreString: string[]	= [];
	let		nbEpisodes				= 0;
	let		listUrlEpisodes: any	= [];
	let		idSelectedSeason		= 0;
	let		selectedEpisode			= 0;
	const	listSource: any			= writable([]);

	interface Season {
		name: string;
		url: string;
		lang: string;
	}

	const	banGenre = ['vostfr', 'vf', 'cardlistanime', 'anime', '-', 'scans', 'film'];
	data.anime?.genre?.map((genre: string) => {
		if (!banGenre.includes(genre.toLowerCase()))
			genreString?.push(genre); 
	});

	function changeSeason(find: boolean)
	{
		fetch(serverUrl + '/api/get_anime_episodes', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			}, 
			body: JSON.stringify({url: data.anime.url, season: data.anime.season[idSelectedSeason].url, serverUrl: window.location.origin}),
		}).then((response) => {
			return response.json();
		}).then((data) => {
			if (!find)
				selectedEpisode = 0;
			nbEpisodes = data.number;
			listUrlEpisodes = data.episodes;
			changeEpisode();
		}).catch(() => {
			nbEpisodes = 0;
			listUrlEpisodes = []
		});
	}

	if (data.anime.progress.find)
	{
		selectedEpisode = data.anime.progress.episode - 1;
		idSelectedSeason = data.anime.season.findIndex((season: Season) => season.url == data.anime.progress.season);
		if (idSelectedSeason == -1)
			idSelectedSeason = 0;
		changeSeason(true);
	}
	else
		changeSeason(false);

	function changeEpisode()
	{
		listSource.update(() => listUrlEpisodes['eps' + (selectedEpisode + 1)]);
	}
</script>

<main class='show-main'>
	<div class='tile left-part'>
		<VideoOverlay srcs={listSource}
			bind:menu={menu}
			selectedEpisode={selectedEpisode}
			idSelectedSeason={idSelectedSeason} 
			allSeasons={data.anime.season}
			progress={data.anime.progress}
			nbEpisodes={nbEpisodes}
		/>
		<div class='description'>
			<div style="display: flex;">
				{#if data.tmdb.poster != '' && !data.tmdb.noData}
					<div class="poster">
						<img src={data.tmdb.poster} alt={data.anime.title} style="width: 100%; object-fit: contain; border-radius: 0.5rem;">
					</div>
				{/if}
				<div style="margin-left: 1rem;">
					<h1 class='title'>{data.tmdb.title ? data.tmdb.title : data.anime.title}</h1>
					<h2 class='original-name'>{data.tmdb.originalName ? data.tmdb.originalName :''}</h2>
					<h3 class='genre'>{genreString.join(', ')}</h3>
					{#if !data.tmdb.noData}
						<p class="overview" >{data.tmdb.overview ? data.tmdb.overview : data.anime.description}</p>
					{/if}
				</div>

			</div>
		</div>
	</div>
	<div class='tile right-part'>
		<select id="seasons" bind:value={idSelectedSeason} on:change={(event) => {
			idSelectedSeason = parseInt((event.target as HTMLSelectElement).value);
			changeSeason(false);
		}}>
			{#if data.anime.season}
				{#each data.anime.season as season, index}
					<option value={index}>{season.name} - {season.lang.toUpperCase()}</option>
				{/each}
			{/if}
		</select>
		<div class='list-episodes'>
			{#if nbEpisodes > 0}
				{#each Array(nbEpisodes) as _, index}
					<button class="no-style-button" on:click={() => selectedEpisode = index}
						style="{selectedEpisode == index ? "background-color: #ccc" : ""}"
						on:click={() => {
							selectedEpisode = index;
							changeEpisode();
						}}
					>
						<p>Episode {index + 1}</p>
					</button>
				{/each}
			{:else}
				<p style="text-align: center; padding: 1rem">Aucun épisode disponible pour le moment</p>
			{/if}
		</div>
	</div>
</main>

<style>
	main {
		display: flex;
		height: 100%;
		width: 100%;
		padding: 1rem;
		position: relative;
		flex-direction: row;
		justify-content: space-between;
		color: #fff;
	}
	.no-style-button {
		background-color: transparent;
		border: none;
		cursor: pointer;
		color: #fff;
		padding: 0.4rem;
		display: flex;
		align-items: center;
		width: 100%;
	}
	.tile {
		border-radius: 0.5rem;
		background-color: #c7c7c75c;
		border: 1px solid #c7c7c72b;
		box-shadow: 0 0 5px #0000003b
	}
	.left-part {
		width: 70%;
		height: 100%;
		margin-right: 1rem;
		overflow: auto;
		padding: 1rem;
	}
	.right-part {
		width: 30%;
		min-width: 200px;
		height: 100%;
		padding: 1rem;
	}
	.description {
		padding: 1rem;
		background-color: #0000003b;
		border-radius: 0 0 0.5rem 0.5rem;
	}
	.title {
		font-size: 1.5rem;
		margin-top: 0.2rem;
	}
	.poster {
		width: 10rem;
		min-width: 10rem;
		max-width: 50%;
		object-fit: contain;
	}
	.original-name {
		font-size: 1rem;
		color: #c7c7c7;
	}
	.genre {
		font-size: 0.8rem;
		color: #c7c7c7;
	}
	.overview {
		font-size: 0.9rem;
		margin-top: 1rem;
		text-align: justify;
	}
	select {
		appearance: none;
		-webkit-appearance: none;
		-moz-appearance: none;
		background: url('/img/select.png') no-repeat right center;
		background-size: 2rem;
	}
	#seasons {
		width: 100%;
		height: 2rem;
		background-color: #0000003b;
		color: #fff;
		border: none;
		border-radius: 0.5rem;
		text-align: center;
	}
	.list-episodes {
		margin-block: 1rem;
		height: calc(100% - 3rem);
		background-color: #0000003b;
		border-radius: 0.5rem;
		overflow: auto;
	}
	.show-main {
		animation: fadeIn 0.5s;
	}
</style>