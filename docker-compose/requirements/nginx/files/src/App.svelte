<script lang="ts">
	import { Router, Route, navigate, Link } from "svelte-routing";
	import '@fortawesome/fontawesome-free/css/all.css';

	import Home from './Home/Home.svelte';
	import Player from './Player/Player.svelte';
	import List from './List/List.svelte';
	import Download from './Download/Download.svelte';
	import Stats from './Stats/Stats.svelte';
	import LeftBar from "./Global/LeftBar.svelte";
	import Login from "./Login/Login.svelte";
	import ChooseUser from "./Login/ChooseUser.svelte";

	const serverUrl = '';
	const cantDirectAccess = ['/player'];
	const location = window.location.pathname;

	let menu: any = {
		selected: -1 as number,
		data: {} as any,
		dominantColor: '' as string,
		user: {
			id: -1,
			name: ''
		},
		selectedGenre: null as string | null
	};

	let genres: string[] = [];
	let showGenreDropdown = false;

	let searchQuery = '';
	let searchResults: any[] = [];
	let showSearchResults = false;
	let searchTimeout: any = null;
	let isSearching = false;

	if (localStorage.getItem('token')) {
		checkToken().then(() => {
			get_name();
			fetchGenres();
			menu.selected = 0;
			if (location === '/')
				navigate('/home', {replace: true});
		}).catch(() => {
			navigate('/', {replace: true});
			history.replaceState(null, 'Login', '/');
			menu.selected = 7;
		});
		init();
	} else {
		navigate('/', {replace: true});
		history.replaceState(null, 'Login', '/');
		menu.selected = 7;
	}

	function init() {
		window.onpopstate = function(event) {
			const location = window.location.pathname;
			if (cantDirectAccess.includes(location))
				navigate('/home');
		}

		window.onload = function() {
			if (cantDirectAccess.includes(location))
				navigate('/home');
			else
				history.pushState(null, 'Aniteve', location);
		}
	}

	function fetchGenres() {
		fetch(serverUrl + '/api/get_all_genres', {
			method: 'GET',
			headers: {
				'Authorization': localStorage.getItem('token') || ''
			}
		})
		.then(res => res.json())
		.then(data => {
			console.log('Genres response:', data);
			if (Array.isArray(data)) {
				genres = data;
			} else {
				console.error('Genres data is not an array:', data);
			}
		})
		.catch(err => console.error('Fetch genres error:', err));
	}

	function get_name() {
		const idUser = localStorage.getItem('idUser');
		if (idUser) {
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
		} else {
			navigate('/choose_user', {replace: true});
			menu.selected = 8;
			history.replaceState(null, 'Aniteve - Choisir un utilisateur', '/choose_user');
		}
	}

	function checkToken() {
		return (new Promise<void>((resolve, reject)=> {
			const token = localStorage.getItem('token');
			if (token) {
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
					else {
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

	function handleGenreClick(genre: string) {
		showGenreDropdown = false;
		menu.selectedGenre = genre;
		navigate('/home');
	}

	function clearGenreFilter() {
		menu.selectedGenre = null;
	}

	function closeDropdowns() {
		showGenreDropdown = false;
		setTimeout(() => {
			if (!document.activeElement?.closest('.search-container')) {
				showSearchResults = false;
			}
		}, 150);
	}

	function handleSearchInput(e: Event) {
		const value = (e.target as HTMLInputElement).value;
		searchQuery = value;

		if (searchTimeout) clearTimeout(searchTimeout);

		if (value.length < 2) {
			searchResults = [];
			showSearchResults = false;
			return;
		}

		isSearching = true;
		searchTimeout = setTimeout(() => {
			fetchSearchResults(value);
		}, 300);
	}

	function fetchSearchResults(query: string) {
		fetch(serverUrl + '/api/search_anime?q=' + encodeURIComponent(query) + '&limit=6', {
			method: 'GET',
			headers: {
				'Authorization': localStorage.getItem('token') || ''
			}
		})
		.then(res => res.json())
		.then(data => {
			searchResults = data;
			showSearchResults = true;
			isSearching = false;
		})
		.catch(err => {
			console.error(err);
			isSearching = false;
		});
	}

	function selectAnime(anime: any) {
		searchQuery = '';
		searchResults = [];
		showSearchResults = false;
		menu.data = anime;
		menu.selected = 4;
		navigate('/player', {replace: true});
	}

	function handleSearchFocus() {
		if (searchResults.length > 0) {
			showSearchResults = true;
		}
	}

	function handleSearchKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			showSearchResults = false;
			(e.target as HTMLInputElement).blur();
		}
	}
</script>

<svelte:window on:click={closeDropdowns} />

<main>
	<Router>
		{#if menu.selected != 7 && menu.selected != -1 && menu.selected != 8}
			<LeftBar bind:menu={menu} />
			<div id="main-content">
				<header id="top-nav">
					<div class="nav-left">
						<Link to="/home" class="nav-link {menu.selected === 0 ? 'active' : ''}">
							Accueil
						</Link>
						<div class="nav-dropdown" on:click|stopPropagation={() => showGenreDropdown = !showGenreDropdown}>
							<span class="nav-link">
								Genres <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 0.3rem;"></i>
							</span>
							{#if showGenreDropdown}
								<div class="dropdown-content">
									{#each genres.slice(0, 15) as genre}
										<button class="dropdown-item" on:click={() => handleGenreClick(genre)}>
											{genre}
										</button>
									{/each}
								</div>
							{/if}
						</div>
					</div>
					<div class="nav-center">
						<div class="search-container" on:click|stopPropagation>
							<div class="search-box">
								<i class="fas fa-search"></i>
								<input
									type="text"
									placeholder="Rechercher un anime..."
									bind:value={searchQuery}
									on:input={handleSearchInput}
									on:focus={handleSearchFocus}
									on:keydown={handleSearchKeydown}
								/>
								{#if searchQuery}
									<button class="clear-btn" on:click={() => { searchQuery = ''; searchResults = []; showSearchResults = false; }}>
										<i class="fas fa-times"></i>
									</button>
								{/if}
							</div>
							{#if showSearchResults}
								<div class="search-results">
									{#if isSearching}
										<div class="search-loading">
											<i class="fas fa-spinner fa-spin"></i>
										</div>
									{:else if searchResults.length === 0}
										<div class="search-empty">
											<p>Aucun résultat pour "{searchQuery}"</p>
										</div>
									{:else}
										{#each searchResults as anime}
											<button class="search-result-item" on:click={() => selectAnime(anime)}>
												<img src={anime.img} alt={anime.title} />
												<div class="result-info">
													<span class="result-title">{anime.title}</span>
													{#if anime.genre && anime.genre.length > 0}
														<span class="result-genre">{anime.genre[0]}</span>
													{/if}
												</div>
											</button>
										{/each}
									{/if}
								</div>
							{/if}
						</div>
					</div>
					</header>
				<div id="content">
					<Route path="/home" let:location>
						<Home bind:menu={menu} />
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
					<Route path="/stats" let:location>
						<Stats bind:menu={menu} />
					</Route>
					<Route path="/choose_user" let:location>
						<ChooseUser bind:menu={menu} />
					</Route>
				</div>
			</div>
		{:else}
			<div id="content-full">
				{#if menu.selected == 7}
					<Route path="/" let:location>
						<Login bind:menu={menu} />
					</Route>
				{/if}
				<Route path="/choose_user" let:location>
					<ChooseUser bind:menu={menu} />
				</Route>
			</div>
		{/if}
	</Router>
</main>

<style>
	main {
		display: flex;
		height: 100vh;
		width: 100vw;
		position: relative;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
		background-color: #0d0d0d;
	}

	#main-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	#top-nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 2rem;
		background-color: transparent;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	.nav-left {
		display: flex;
		align-items: center;
		gap: 2rem;
	}

	:global(.nav-link) {
		color: rgba(255, 255, 255, 0.7);
		text-decoration: none;
		font-size: 0.9rem;
		font-weight: 500;
		transition: color 0.2s;
		cursor: pointer;
	}

	:global(.nav-link:hover), :global(.nav-link.active) {
		color: #ffffff;
	}

	.nav-dropdown {
		position: relative;
	}

	.dropdown-content {
		position: absolute;
		top: 100%;
		left: 0;
		margin-top: 0.5rem;
		background-color: #1a1a1a;
		border-radius: 0.5rem;
		padding: 0.5rem 0;
		min-width: 180px;
		box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
		z-index: 100;
		max-height: 400px;
		overflow-y: auto;
	}

	.dropdown-item {
		display: block;
		width: 100%;
		padding: 0.6rem 1rem;
		color: rgba(255, 255, 255, 0.8);
		background: none;
		border: none;
		text-align: left;
		cursor: pointer;
		font-size: 0.85rem;
		transition: background-color 0.2s;
	}

	.dropdown-item:hover {
		background-color: rgba(255, 255, 255, 0.1);
		color: #ffffff;
	}

	.nav-center {
		flex: 1;
		display: flex;
		justify-content: center;
		max-width: 450px;
		margin: 0 2rem;
	}

	.search-container {
		position: relative;
		width: 100%;
	}

	.search-box {
		display: flex;
		align-items: center;
		background-color: rgba(255, 255, 255, 0.08);
		border-radius: 0.5rem;
		padding: 0.6rem 1rem;
		width: 100%;
		transition: background-color 0.2s;
	}

	.search-box:hover, .search-box:focus-within {
		background-color: rgba(255, 255, 255, 0.12);
	}

	.search-box i {
		color: rgba(255, 255, 255, 0.5);
		margin-right: 0.75rem;
		font-size: 0.9rem;
	}

	.search-box input {
		background: none;
		border: none;
		color: #ffffff;
		width: 100%;
		font-size: 0.9rem;
		outline: none;
	}

	.search-box input::placeholder {
		color: rgba(255, 255, 255, 0.4);
	}

	.clear-btn {
		background: none;
		border: none;
		color: rgba(255, 255, 255, 0.4);
		cursor: pointer;
		padding: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.2s;
	}

	.clear-btn:hover {
		color: rgba(255, 255, 255, 0.8);
	}

	.search-results {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		margin-top: 0.5rem;
		background-color: #1a1a1a;
		border-radius: 0.75rem;
		padding: 0.5rem;
		box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
		z-index: 200;
		max-height: 400px;
		overflow-y: auto;
	}

	.search-loading, .search-empty {
		padding: 1.5rem;
		text-align: center;
		color: rgba(255, 255, 255, 0.5);
	}

	.search-loading i {
		font-size: 1.5rem;
	}

	.search-empty p {
		font-size: 0.9rem;
	}

	.search-result-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		width: 100%;
		padding: 0.6rem;
		background: none;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: background-color 0.2s;
		text-align: left;
	}

	.search-result-item:hover {
		background-color: rgba(255, 255, 255, 0.08);
	}

	.search-result-item img {
		width: 45px;
		height: 60px;
		object-fit: cover;
		border-radius: 0.375rem;
		flex-shrink: 0;
	}

	.result-info {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
		min-width: 0;
	}

	.result-title {
		font-size: 0.9rem;
		font-weight: 500;
		color: #ffffff;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.result-genre {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.5);
	}

	#content {
		flex: 1;
		overflow: hidden;
	}

	#content-full {
		flex: 1;
		width: 100%;
		height: 100%;
	}
</style>
