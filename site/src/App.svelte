<script lang="ts">
	import { Router, Route, navigate } from "svelte-routing";

	import Home from './Home/Home.svelte';
	import Anime from './Anime/Anime.svelte';
	import Player from './Player/Player.svelte';
	import Search from './Search/Search.svelte';
	import List from './List/List.svelte';
	import Downlaod from './Download/Download.svelte';
	import LeftBar from "./Global/LeftBar.svelte";
	import downloader from "./Global/Downloader";

	const cantDirectAccess = ['/anime', '/player'];
	const location = window.location.pathname;

	let menu: any = {
		selected: 0 as number,
		data: {} as any,
		dominantColor: '' as string,
		downloader: downloader,
	}; // 0: home, 1: search,  2: list, 3: anime, 4: player, 6: Download

	window.onpopstate = function(event)
	{
		const location = window.location.pathname;
		if (cantDirectAccess.includes(location))
			navigate('/');
	}

	window.onload = function()
	{
		if (cantDirectAccess.includes(location))
			navigate('/');
		else
			history.pushState(null, 'Anime', location);
	}
</script>


<main>
	<Router>
		<LeftBar bind:menu={menu} />
		<div id="content">
			<Route path="/" let:location>
				<Home bind:menu={menu} />
			</Route>
			<Route path="/search" let:location>
				<Search bind:menu={menu} />
			</Route>
			<Route path="/anime" let:location>
				<Anime bind:menu={menu} />
			</Route>
			<Route path="/player" let:location>
				<Player bind:menu={menu} />
			</Route>
			<Route path="/list" let:location>
				<List bind:menu={menu} />
			</Route>
			<Route path="/download" let:location>
				<Downlaod bind:menu={menu} />
			</Route>
		</div>
	</Router>
</main>

<style>
	main {
		display: flex;
		height: 100vh;
		width: 100vw;
		padding: 1rem;
		position: relative;
		font-family: 'Roboto', sans-serif;
	}
	#content {
		flex: 1;
		overflow: hidden;
	}
</style>
