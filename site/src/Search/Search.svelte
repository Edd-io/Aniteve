<script lang="ts">
	import ItemAnime from "./ItemAnime.svelte";

	export let menu: any;

	let animeList: any = [];
	let showedAnimeList: any = [];
	let animeSelected: any = {bool: false, id: 0};
	let counter: number = 0;

	menu.dominantColor = '#c7c7c75c';
	menu.selected = 1;
	fetch('http://localhost:8080/api/get_all_anime')
	.then(res => res.json())
	.then(data => {
		animeList = data;
		showedAnimeList = animeList;
	})
	.catch(err => console.error(err));

	function filterList()
	{
		const searchInput = document.querySelector('input');
		const searchValue = searchInput?.value.toLowerCase();

		if (!searchValue)
			showedAnimeList = animeList;
		else
		{
			showedAnimeList = [];
			for (let i = 0; i < animeList.length; i++)
			{
				if (animeList[i].title.toLowerCase().includes(searchValue))
					showedAnimeList.push(animeList[i]);
				else if (animeList[i].alternative_title?.toLowerCase().includes(searchValue))
					showedAnimeList.push(animeList[i]);
				else
					continue
			}
			counter++;
		}	
	}
</script>

<main>
	
		<div class="top-bar">
			<div class="search-input">
				<img src="../assets/img/search.png" alt="search" />
				<input type="text" placeholder="Rechercher un anime..." on:input={filterList} />
			</div>
		</div>
		{#if showedAnimeList.length > 0}
			{#key counter}
				<div class="anime-list">
					{#each showedAnimeList as anime (anime.id)}
						<ItemAnime animeData={anime} bind:animeSelected={animeSelected} bind:menu={menu} />
					{/each}
				</div>
			{/key}
		{/if}
</main>

<style>
	main {
		flex: 1;
		height: 100%;
	}
	.top-bar {
		width: 100%;
		height: 2.5rem;
	}
	.top-bar .search-input {
		border-radius: 0.5rem;
		display: flex;
		align-items: center;
		padding: 0 10px;
		height: 90%;
		width: 97%;
		margin-inline: auto;
		background-color: #c7c7c75c;
		border: 1px solid #c7c7c72b;
		box-shadow: 0 0 5px #0000003b;
		color: #fff;
	}

	.top-bar .search-input input::placeholder {
		color: rgb(159, 159, 159);
	}
	.top-bar .search-input img {
		height: 75%;
		margin-block: auto;
		margin-right: 0.5rem;
	}
	.top-bar .search-input input {
		background-color: transparent;
		border: none;
		color: #fff;
		width: 100%;
		height: 100%;
	}
	.top-bar .search-input input:focus {
		outline: none;
	}
	.anime-list {
		overflow-y: scroll;
		width: 100%;
		max-height: calc(100% - 3.5rem);
		margin-block: 0.5rem;
		display: flex;
		flex-direction: row;
		flex-wrap: wrap;
		justify-content: center;
	}
</style>