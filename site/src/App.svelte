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
	import ChooseUser from "./Login/ChooseUser.svelte";

	const	serverUrl = 'http://localhost:8080';
	const	cantDirectAccess = ['/anime', '/player'];
	const	location = window.location.pathname;

	let menu: any = {
		selected: -1 as number,
		data: {} as any,
		dominantColor: '' as string,
		user: {
			id: 0,
			name: ''
		}
	}; // 0: home, 1: search,  2: list, 3: anime, 4: player, 6: Download, 7: Login, 8: ChooseUser

	if (localStorage.getItem('token'))
	{
		checkToken().then(() => {
			get_name();
			if (location === '/')
				navigate('/home', {replace: true});
		}).catch(() => {
			navigate('/', {replace: true});
			history.replaceState(null, 'Login', '/');
			menu.selected = 7;
		});
		init();
	}
	else
	{
		navigate('/', {replace: true});
		history.replaceState(null, 'Login', '/');
		menu.selected = 7;
	}

	function init()
	{
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
				history.pushState(null, 'Aniteve', location);
		}
	}

	function get_name()
	{
		const idUser = localStorage.getItem('idUser');
		if (idUser)
		{
			fetch(serverUrl + '/api/get_name', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': localStorage.getItem('token') || '',
				},
				body: JSON.stringify({ id: idUser })
			})
			.then(res => res.json())
			.then(data => {
				menu.user.id = parseInt(idUser);
				menu.user.name = data.name;
			})
			.catch(() => {
				console.warn('Error: get_name');
				localStorage.removeItem('idUser');
				localStorage.removeItem('token');
				navigate('/', {replace: true});
				menu.selected = 7;
				history.replaceState(null, 'Aniteve - Choisir un utilisateur', '/choose_user');
			});
		}
		else
		{
			navigate('/choose_user', {replace: true});
			menu.selected = 8;
			history.replaceState(null, 'Aniteve - Choisir un utilisateur', '/choose_user');
		}
	}

	function checkToken()
	{
		return (new Promise<void>((resolve, reject)=> {
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
						resolve();
					else
					{
						localStorage.removeItem('token');
						reject();
					}
				})
				.catch(() => {
					localStorage.removeItem('token');
					reject();
				});
			}
		}));
	}
</script>


<main>
	<Router>
		{#if menu.selected != 7 && menu.selected != -1 && menu.selected != 8}
			<LeftBar bind:menu={menu} />
		{/if}
		<div id="content">
			{#if menu.selected == 7}
				<Route path="/" let:location>
					<Login bind:menu={menu} />
				</Route>
			{/if}
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
			<Route path="/choose_user" let:location>
				<ChooseUser bind:menu={menu} />
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
