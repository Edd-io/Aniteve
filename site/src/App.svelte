<script lang="ts">
	import { Router, Route, navigate } from "svelte-routing";

	import Home from './Home/Home.svelte';
	import Anime from './Anime/Anime.svelte';
	import Player from './Player/Player.svelte';
	import Search from './Search/Search.svelte';
	import List from './List/List.svelte';
	import Download from './Download/Download.svelte';
	import LeftBar from "./Global/LeftBar.svelte";
    import Login from "./Login/Login.svelte";

	const serverUrl = 'http://localhost:8080';
	const cantDirectAccess = ['/anime', '/player'];
	const location = window.location.pathname;

	let menu: any = {
		selected: -1 as number,
		data: {} as any,
		dominantColor: '' as string,
	}; // 0: home, 1: search,  2: list, 3: anime, 4: player, 6: Download, 7: Login

	window.onpopstate = function(event)
	{
		const location = window.location.pathname;
		if (cantDirectAccess.includes(location))
			navigate('/home');
	}

	window.onload = function()
	{
		if (cantDirectAccess.includes(location))
			navigate('/home');
		else
			history.pushState(null, 'Anime', location);
	}

	console.log('token: ', localStorage.getItem('token'));
	if (localStorage.getItem('token'))
		checkToken();
	else
	{
		navigate('/', {replace: true});
		history.replaceState(null, 'Login', '/');
		menu.selected = 7;
	}

	function checkToken()
	{
		const token = localStorage.getItem('token');
		if (token)
		{
			fetch(serverUrl + '/api/check_token', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ token })
			})
			.then(res => res.json())
			.then(data => {
				if (data.status === 'success')
				{
					setTimeout(() => {
						navigate('/home', {replace: true});
						menu.selected = 0;
						history.replaceState(null, 'Login', '/');
					}, 200);
				}
				else
					localStorage.removeItem('token');
			})
			.catch(() => {
				localStorage.removeItem('token');
			});
		}
	}
</script>


<main>
	<Router>
		{#if menu.selected != 7 && menu.selected != -1}
			<LeftBar bind:menu={menu} />
		{/if}
		<div id="content">
			<Route path="/" let:location>
				<Login bind:menu={menu} />
			</Route>
			<Route path="/home" let:location>
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
				<Download bind:menu={menu} />
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
