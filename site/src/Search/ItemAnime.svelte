<script lang='ts'>
	export let animeData: any = [];
	export let animeSelected: any = {bool: false, id: 0};
	export let menu: any;
	
	function hideAllTiles()
	{
		animeSelected.bool = true;
		animeSelected.id = animeData.id;
		const tiles = document.querySelectorAll('.tile');
		tiles.forEach(tile => {
			const htmlTile = tile as HTMLElement;
			if (htmlTile.getAttribute('itemId') == animeData.id)
			{
				const copy = htmlTile.cloneNode(true) as HTMLElement;
				copy.style.opacity = '0';
				const pos = htmlTile.getBoundingClientRect();
				
				htmlTile.parentNode?.insertBefore(copy, htmlTile);
				htmlTile.style.position = 'absolute';
				htmlTile.style.top = `calc(${pos.top}px - 1rem)`;
				htmlTile.style.left = pos.left + 'px';
				htmlTile.style.width = pos.width + 'px';
				htmlTile.style.height = pos.height + 'px';
				htmlTile.style.zIndex = '999';
				setTimeout(() => {
					htmlTile.style.animation = 'choose 0.5s';
					htmlTile.style.opacity = '0';
					setTimeout(() => {
						menu.data = animeData;
						menu.selected = 3;
					}, 400);
				}, 500);
				return;
			}
			htmlTile.style.animation = 'fadeOut 0.5s';
			htmlTile.style.zIndex = '0';
			setTimeout(() => {
				htmlTile.style.opacity = '0';
			}, 450);
		});
	}
</script>

<button class="tile no-style-button {!animeSelected.bool ? 'tile-hover' : 'tile-hover-selected'}" on:click={() => {
	!animeSelected.bool ? hideAllTiles() : null;
	animeSelected.bool = true;
}} itemId={animeData.id}>
	<div class="img-container">
		<img src="{animeData.img}" alt="{animeData.title}" />
	</div>
	<div class="tile-content">
		<p>{animeData.title.length > 40 ? animeData.title.slice(0, 40) + '...' : animeData.title}</p>
	</div>
</button>

<style>
	.no-style-button {
		background-color: transparent;
		border: none;
		cursor: pointer;
		color: #fff;
		padding: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.tile {
		width: 14rem;
		height: 12rem;
		border-radius: 0.5rem;
		transition: background-color 0.2s, scale 0.2s;
		margin: 0.5rem;
		padding: 0.5rem;
		padding-bottom: 0;
		background-color: #c7c7c75c;
		border: 1px solid #c7c7c72b;
		box-shadow: 0 0 5px #0000003b;
	}
	.tile-hover:hover {
		background-color: #c7c7c7af;
		scale: 1.05;
	}
	.tile-hover-selected {
		background-color: #c7c7c7af;
		scale: 1.05;
		cursor: default;
	}
	.img-container {
		width: 100%;
		height: 10rem;
	}
	.tile img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		border-radius: 0.5rem;
	}
	.tile-content {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 4rem;
	}
	p {
		text-align: center;
		margin: 0.5rem;
		font-size: 0.9rem;
	}
</style>