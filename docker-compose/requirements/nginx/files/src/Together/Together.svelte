<script lang='ts'>
	import { onMount, onDestroy, tick } from 'svelte';
	import { io } from 'socket.io-client';
	import '@fortawesome/fontawesome-free/css/all.css';

	export let menu: any;

	const serverUrl = '';
	const banGenre = ['vostfr', 'vf', 'cardlistanime', 'anime', '-', 'scans', 'film'];

	// States
	let view = 'lobby'; // 'lobby' | 'room'
	let rooms: any[] = [];
	let currentRoom: any = null;
	let socket: any = null;
	let isHost = false;
	let users: any[] = [];

	// Video states
	let video: any = null;
	let paused = true;
	let volume = parseFloat(localStorage.getItem('player_volume') || '0.75');
	let currentTime = 0;
	let duration = 0;
	let buffering = false;
	let muted = localStorage.getItem('player_muted') === 'true';
	let showOverlay = false;
	let animationOverlay = false;
	let timeoutOverlay: any = null;
	let src = '';
	let isSyncing = false;
	let lastTimeSync = 0;

	// Current playing anime info (for progress tracking)
	let currentAnimeId: number | null = null;
	let currentAnimeTitle: string | null = null;
	let currentEpisode: number = 0;
	let currentSeasonUrl: string | null = null;
	let currentPoster: string = '';

	// Anime selection states
	let showAnimeSelector = false;
	let allSeasons: any[] = [];
	let selectedAnime: any = null;
	let selectedSeasonIdx = 0;
	let selectedEpisode = 0;
	let nbEpisodes = 0;
	let listUrlEpisodes: any = [];
	let srcsList: string[] = [];
	let selectedSource = 0;
	let searchQuery = '';
	let searchResults: any[] = [];
	let isSearching = false;
	let searchTimeout: any = null;
	let errorMessage = '';
	let errorTimeout: any = null;
	let watchingAnimes: any[] = [];

	menu.selected = 7;
	menu.dominantColor = '#0d0d0d';

	function showError(message: string) {
		errorMessage = message;
		if (errorTimeout) clearTimeout(errorTimeout);
		errorTimeout = setTimeout(() => {
			errorMessage = '';
		}, 5000);
	}

	function handleFullscreenChange() {
		isFullscreen = !!document.fullscreenElement;
	}

	let progressInterval: any = null;

	onMount(() => {
		fetchRooms();
		connectSocket();
		document.addEventListener('fullscreenchange', handleFullscreenChange);

		// Save progress every 10 seconds
		progressInterval = setInterval(() => {
			if (!video || !currentAnimeId || !duration || video.paused) return;

			const progress = (video.currentTime / duration) * 100;
			fetch(serverUrl + '/api/update_progress', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': localStorage.getItem('token') || ''
				},
				body: JSON.stringify({
					id: currentAnimeId,
					episode: currentEpisode,
					totalEpisode: nbEpisodes || currentEpisode,
					seasonId: selectedSeasonIdx,
					allSeasons: allSeasons.length > 0 ? allSeasons : [{ url: currentSeasonUrl }],
					progress: progress || 0,
					poster: currentPoster,
					idUser: menu.user.id
				})
			}).catch(console.error);
		}, 10000);
	});

	onDestroy(() => {
		if (progressInterval) clearInterval(progressInterval);
		document.removeEventListener('fullscreenchange', handleFullscreenChange);
		if (socket) {
			socket.disconnect();
		}
		if (video) {
			video.pause();
			video.removeAttribute('src');
			video.load();
		}
	});

	function connectSocket() {
		socket = io(window.location.origin, {
			transports: ['websocket', 'polling']
		});

		socket.on('connect', () => {
			console.log('Socket connected');
		});

		socket.on('room_state', async (data: any) => {
			console.log('[WS] Received room_state:', data);
			currentRoom = data;
			users = data.users;
			isHost = data.users.find((u: any) => u.user_id === menu.user.id)?.is_host || false;
			console.log('[WS] Room state updated. Users:', users.length, 'isHost:', isHost);
			view = 'room'; // Change view after receiving room state

			// Fetch watching animes if host
			if (isHost) {
				fetchWatchingAnimes();
			}

			// Wait for DOM to update before applying video state
			await tick();

			// Apply video state
			if (data.video_state.source) {
				applySyncedVideoState(data.video_state);
			}
		});

		socket.on('user_joined', (data: any) => {
			console.log('[WS] User joined:', data.username, 'Total users:', data.users.length);
			users = data.users;
		});

		socket.on('user_left', (data: any) => {
			console.log('[WS] User left. Updating users list');
			users = data.users;
			// Check if we became host after someone left
			const myUser = data.users.find((u: any) => u.user_id === menu.user.id);
			if (myUser) {
				const wasHost = isHost;
				isHost = myUser.is_host;
				if (!wasHost && isHost) {
					console.log('[WS] We are now the host!');
				}
			}
		});

		socket.on('video_state', (data: any) => {
			applySyncedVideoState(data);
		});

		socket.on('host_transferred', (data: any) => {
			console.log('[WS] Host transferred:', data);
			currentRoom = data;
			users = data.users;
			const myUser = data.users.find((u: any) => u.user_id === menu.user.id);
			if (myUser) {
				isHost = myUser.is_host;
				console.log('[WS] isHost updated to:', isHost);
				if (isHost) {
					fetchWatchingAnimes();
				}
			}
		});

		socket.on('error', (data: any) => {
			alert(data.error);
		});
	}

	function applySyncedVideoState(state: any) {
		if (!video) return;

		// Detect if play state changed
		const playStateChanged = state.is_playing !== undefined &&
			((state.is_playing && video.paused) || (!state.is_playing && !video.paused));

		// Always apply play/pause state immediately (never ignore)
		if (state.is_playing !== undefined) {
			if (state.is_playing && video.paused) {
				video.play().catch(console.error);
			} else if (!state.is_playing && !video.paused) {
				video.pause();
			}
		}

		// Force time sync on play/pause change to avoid desync
		if (playStateChanged && state.current_time !== undefined) {
			video.currentTime = state.current_time;
			return;
		}

		// Skip time/source sync if already syncing to avoid loops
		if (isSyncing) return;

		isSyncing = true;

		// Update source if changed
		if (state.source && state.source !== src) {
			src = state.source;
			putSrc(state.source);
		}

		// Update current anime info for progress tracking
		if (state.anime_id !== undefined) currentAnimeId = state.anime_id;
		if (state.anime_title !== undefined) currentAnimeTitle = state.anime_title;
		if (state.episode !== undefined) currentEpisode = state.episode;
		if (state.season_url !== undefined) currentSeasonUrl = state.season_url;
		if (state.poster !== undefined) currentPoster = state.poster;

		// Sync time (only if difference > 2 seconds)
		if (state.current_time !== undefined && Math.abs(video.currentTime - state.current_time) > 2) {
			video.currentTime = state.current_time;
		}

		setTimeout(() => {
			isSyncing = false;
		}, 100);
	}

	function fetchRooms() {
		fetch(serverUrl + '/api/rooms', {
			method: 'GET',
			headers: {
				'Authorization': localStorage.getItem('token') || ''
			}
		})
		.then(res => res.json())
		.then(data => {
			rooms = data.rooms || [];
		})
		.catch(console.error);
	}

	function createRoom() {
		fetch(serverUrl + '/api/rooms/create', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || ''
			},
			body: JSON.stringify({
				user_id: menu.user.id,
				username: menu.user.name
			})
		})
		.then(res => res.json())
		.then(data => {
			if (data.error) {
				showError(data.error);
			} else {
				joinRoom(data.room_id);
			}
		})
		.catch(err => {
			console.error(err);
			showError('Erreur lors de la création de la room');
		});
	}

	function joinRoom(roomId: string) {
		console.log('[WS] Joining room:', roomId, 'as', menu.user.name);
		socket.emit('join_room', {
			room_id: roomId,
			user_id: menu.user.id,
			username: menu.user.name
		});
		// Note: view will be changed to 'room' when we receive room_state
	}

	function leaveRoom() {
		socket.emit('leave_room');
		view = 'lobby';
		currentRoom = null;
		users = [];
		isHost = false;
		fetchRooms();
	}

	function togglePlay() {
		if (!isHost || !video) return;

		if (video.paused) {
			video.play();
			socket.emit('update_video', {
				current_time: video.currentTime,
				is_playing: true
			});
		} else {
			video.pause();
			socket.emit('update_video', {
				current_time: video.currentTime,
				is_playing: false
			});
		}
	}

	function handleTimeUpdate() {
		if (!video) return;
		currentTime = video.currentTime;

		// Only host sends periodic time updates (throttled to every 3 seconds)
		const now = Date.now();
		if (isHost && !video.paused && !isSyncing && (now - lastTimeSync > 3000)) {
			lastTimeSync = now;
			socket.emit('update_video', {
				current_time: video.currentTime,
				is_playing: true
			});
		}
	}

	function handleSeeking() {
		if (!isHost || !video) return;

		socket.emit('update_video', {
			current_time: video.currentTime,
			is_playing: !video.paused
		});
	}

	function transferHost(userId: number) {
		socket.emit('transfer_host', {
			new_host_user_id: userId
		});
	}

	let isFullscreen = false;
	let videoContainer: HTMLElement;

	function toggleFullscreen() {
		if (!videoContainer) return;

		if (!document.fullscreenElement) {
			videoContainer.requestFullscreen().then(() => {
				isFullscreen = true;
			}).catch(console.error);
		} else {
			document.exitFullscreen().then(() => {
				isFullscreen = false;
			}).catch(console.error);
		}
	}

	function putSrc(source: string) {
		if (!video) return;

		let currentSrc: string;
		if (source.includes('/api/video?')) {
			currentSrc = source.replace(/^https?:\/\/[^/]+/, '');
		} else {
			const urlWithoutProtocol = source.replace(/^https?:\/\//, '');
			currentSrc = serverUrl + '/api/video?' + urlWithoutProtocol;
		}
		video.src = currentSrc;
		video.load();
	}

	// Anime selection functions
	function openAnimeSelector() {
		if (!isHost) return;
		showAnimeSelector = true;
	}

	function selectAnimeFromList(anime: any) {
		selectedAnime = anime;
		fetchSeasons(anime);
	}

	function fetchSeasons(anime: any) {
		fetch(serverUrl + '/api/get_anime_season', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || ''
			},
			body: JSON.stringify({ url: anime.url, serverUrl: serverUrl })
		})
		.then(res => {
			if (!res.ok) {
				throw new Error(`Erreur serveur: ${res.status}`);
			}
			return res.json();
		})
		.then(data => {
			if (data.error) {
				throw new Error(data.error);
			}
			allSeasons = data.season || [];
			if (allSeasons.length > 0) {
				changeSeason();
			} else {
				showError('Aucune saison trouvée pour cet anime');
				selectedAnime = null;
			}
		})
		.catch(err => {
			console.error(err);
			showError(`Erreur lors du chargement des saisons: ${err.message}`);
			selectedAnime = null;
		});
	}

	function changeSeason() {
		if (!allSeasons.length) return;

		fetch(serverUrl + '/api/get_anime_episodes', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || ''
			},
			body: JSON.stringify({
				url: selectedAnime.url,
				season: allSeasons[selectedSeasonIdx].url,
				serverUrl: window.location.origin
			})
		})
		.then(res => {
			if (!res.ok) {
				throw new Error(`Erreur serveur: ${res.status}`);
			}
			return res.json();
		})
		.then(data => {
			if (data.error) {
				throw new Error(data.error);
			}
			nbEpisodes = data.number || 0;
			listUrlEpisodes = data.episodes || [];
			selectedEpisode = 0;
			updateEpisodeSources();
		})
		.catch(err => {
			console.error(err);
			showError(`Erreur lors du chargement des épisodes: ${err.message}`);
		});
	}

	function updateEpisodeSources() {
		srcsList = listUrlEpisodes['eps' + (selectedEpisode + 1)] || [];
		selectedSource = 0;
	}

	function changeSource() {
		if (!isHost || srcsList.length === 0) return;

		fetch(srcsList[selectedSource], {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || ''
			},
			body: JSON.stringify({ serverUrl: window.location.origin })
		})
		.then(res => {
			if (!res.ok) {
				throw new Error(`Erreur serveur: ${res.status}`);
			}
			return res.json();
		})
		.then(data => {
			if (data.error) {
				throw new Error(data.error);
			}
			const source = data.src;
			src = source;
			putSrc(source);

			// Update current anime info for progress tracking
			currentAnimeId = selectedAnime.id;
			currentAnimeTitle = selectedAnime.title;
			currentEpisode = selectedEpisode + 1;
			currentSeasonUrl = allSeasons[selectedSeasonIdx].url;
			currentPoster = selectedAnime.img || '';

			// Notify other users
			socket.emit('update_video', {
				source: source,
				current_time: 0,
				is_playing: false,
				anime_id: currentAnimeId,
				anime_title: currentAnimeTitle,
				episode: currentEpisode,
				season_url: currentSeasonUrl,
				poster: currentPoster
			});

			showAnimeSelector = false;
		})
		.catch(err => {
			console.error(err);
			showError(`Erreur lors du chargement de la source vidéo: ${err.message}`);
		});
	}

	function handleVolumeChange(e: Event) {
		if (!video) return;
		volume = parseFloat((e.target as HTMLInputElement).value);
		video.volume = volume;
		localStorage.setItem('player_volume', volume.toString());
		if (volume > 0 && muted) {
			muted = false;
			video.muted = false;
			localStorage.setItem('player_muted', 'false');
		}
	}

	function handleSearchInput(e: Event) {
		const value = (e.target as HTMLInputElement).value;
		searchQuery = value;

		if (searchTimeout) clearTimeout(searchTimeout);

		if (value.length < 2) {
			searchResults = [];
			return;
		}

		isSearching = true;
		searchTimeout = setTimeout(() => {
			fetchSearchResults(value);
		}, 300);
	}

	function fetchSearchResults(query: string) {
		fetch(serverUrl + '/api/search_anime?q=' + encodeURIComponent(query) + '&limit=8', {
			method: 'GET',
			headers: {
				'Authorization': localStorage.getItem('token') || ''
			}
		})
		.then(res => res.json())
		.then(data => {
			searchResults = data;
			isSearching = false;
		})
		.catch(err => {
			console.error(err);
			isSearching = false;
		});
	}

	function fetchWatchingAnimes() {
		fetch(serverUrl + '/api/get_all_progress', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || ''
			},
			body: JSON.stringify({ idUser: menu.user.id })
		})
		.then(res => res.json())
		.then(data => {
			// Filter only watching (completed = 0) and limit to recent ones
			watchingAnimes = (data || []).filter((a: any) => a.completed === 0).slice(0, 10);
			console.log('[Together] Watching animes:', watchingAnimes);
		})
		.catch(console.error);
	}

	function selectWatchingAnime(item: any) {
		// Set the selected anime info (data is nested: item.anime contains anime info)
		selectedAnime = {
			id: item.anime.id,
			title: item.anime.title,
			url: item.anime.url,
			img: item.poster || item.anime.img
		};

		// Fetch seasons and set the correct one
		fetch(serverUrl + '/api/get_anime_season', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || ''
			},
			body: JSON.stringify({ url: item.anime.url, serverUrl: serverUrl })
		})
		.then(res => res.json())
		.then(data => {
			allSeasons = data.season || [];
			// Find the season index by URL
			selectedSeasonIdx = allSeasons.findIndex((s: any) => s.url === item.season);
			if (selectedSeasonIdx === -1) selectedSeasonIdx = 0;
			selectedEpisode = item.episode - 1;

			// Fetch episodes and open selector
			changeSeason();
			showAnimeSelector = true;
		})
		.catch(err => {
			console.error(err);
			showError('Erreur lors du chargement de l\'anime');
		});
	}

	function handleMouseMove() {
		if (!src) return;

		if (timeoutOverlay) clearTimeout(timeoutOverlay);
		animationOverlay = true;
		showOverlay = true;

		timeoutOverlay = setTimeout(() => {
			animationOverlay = false;
			setTimeout(() => showOverlay = false, 200);
		}, 3000);
	}

	function handleProgressClick(event: MouseEvent) {
		if (!isHost || !video) return;
		const bar = event.currentTarget as HTMLElement;
		const percent = (event.clientX - bar.getBoundingClientRect().left) / bar.offsetWidth;
		video.currentTime = percent * duration;
		socket.emit('update_video', {
			current_time: video.currentTime,
			is_playing: !video.paused
		});
	}

	function handleVideoClick() {
		if (!isHost) return;
		togglePlay();
	}

	function secondsToHms(d: number): string {
		const h = Math.floor(d / 3600);
		const m = Math.floor(d % 3600 / 60);
		const s = Math.floor(d % 60);
		return (h > 0 ? `${h}:` : '') + `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
	}

	function toggleMute() {
		muted = !muted;
		if (video) video.muted = muted;
		localStorage.setItem('player_muted', muted.toString());
	}
</script>

<div id="together-container">
	{#if errorMessage}
		<div class="error-toast">
			<i class="fas fa-exclamation-circle"></i>
			<span>{errorMessage}</span>
			<button class="close-error" on:click={() => errorMessage = ''}>
				<i class="fas fa-times"></i>
			</button>
		</div>
	{/if}

	{#if view === 'lobby'}
		<div class="lobby">
			<h1>Regarder Ensemble</h1>
			<p class="subtitle">Créez ou rejoignez une room pour regarder un anime avec vos amis</p>

			<button class="create-room-btn" on:click={createRoom}>
				<i class="fas fa-plus"></i>
				Créer une room
			</button>

			<div class="rooms-list">
				<h2>Rooms disponibles</h2>
				{#if rooms.length === 0}
					<p class="empty-state">Aucune room disponible. Créez-en une !</p>
				{:else}
					{#each rooms as room}
						<div class="room-card">
							<div class="room-info">
								<h3>{room.name}</h3>
								<p>{room.user_count} {room.user_count > 1 ? 'utilisateurs' : 'utilisateur'}</p>
							</div>
							<button class="join-btn" on:click={() => joinRoom(room.room_id)}>
								Rejoindre
							</button>
						</div>
					{/each}
				{/if}
			</div>
		</div>
	{:else}
		<div class="room-view">
			<div class="room-header">
				<div class="room-title">
					<h2>{currentRoom?.name || 'Room'}</h2>
					{#if isHost}
						<span class="host-badge">Hôte</span>
					{/if}
				</div>
				<button class="leave-btn" on:click={leaveRoom}>
					<i class="fas fa-sign-out-alt"></i>
					Quitter
				</button>
			</div>

			<div class="room-content">
				<div class="video-section">
					<div
						class="video-container"
						class:fullscreen={isFullscreen}
						bind:this={videoContainer}
						on:mousemove={handleMouseMove}
						on:dblclick={toggleFullscreen}
					>
						<video
							bind:this={video}
							on:timeupdate={handleTimeUpdate}
							on:seeked={handleSeeking}
							on:loadedmetadata={() => duration = video.duration}
							on:waiting={() => buffering = true}
							on:canplay={() => { buffering = false; video.volume = volume; video.muted = muted; }}
							on:play={() => paused = false}
							on:pause={() => paused = true}
							on:click={handleVideoClick}
						></video>

						{#if buffering && src}
							<div class="loader-overlay">
								<i class="fas fa-spinner fa-spin"></i>
							</div>
						{/if}

						{#if !src}
							<div class="no-video-overlay">
								<i class="fas fa-film"></i>
								<p>Aucune vidéo sélectionnée</p>
								{#if isHost}
									<button on:click={openAnimeSelector}>
										Choisir un anime
									</button>
								{:else}
									<p class="wait-message">En attente que l'hôte choisisse un anime...</p>
								{/if}
							</div>
						{/if}

						{#if showOverlay && src}
							<div class="controls-overlay" class:visible={animationOverlay}>
								<div class="progress-bar" on:click={handleProgressClick}>
									<div class="progress" style="width: {duration ? (currentTime / duration) * 100 : 0}%"></div>
								</div>
								<div class="controls">
									{#if isHost}
										<button on:click={togglePlay}>
											<i class="fas fa-{paused ? 'play' : 'pause'}"></i>
										</button>
									{/if}
									<div class="volume-control">
										<button on:click={toggleMute}>
											<i class="fas fa-{muted ? 'volume-mute' : 'volume-up'}"></i>
										</button>
										<input
											type="range"
											min="0"
											max="1"
											step="0.01"
											bind:value={volume}
											on:input={handleVolumeChange}
										/>
									</div>
									<span class="time">{secondsToHms(currentTime)} / {secondsToHms(duration)}</span>
									<div class="spacer"></div>
									{#if isHost}
										<button on:click={openAnimeSelector}>
											<i class="fas fa-list"></i>
										</button>
									{/if}
									<button on:click={toggleFullscreen}>
										<i class="fas fa-{isFullscreen ? 'compress' : 'expand'}"></i>
									</button>
								</div>
							</div>
						{/if}
					</div>

					{#if isHost && watchingAnimes.length > 0}
						<div class="watching-section">
							<h3>Continuer à regarder</h3>
							<div class="watching-list">
								{#each watchingAnimes as item}
									<button class="watching-item" on:click={() => selectWatchingAnime(item)}>
										<img src={item.poster || item.anime.img} alt={item.anime.title} />
										<div class="watching-info">
											<span class="watching-title">{item.anime.title}</span>
											<span class="watching-episode">EP {item.episode}</span>
										</div>
									</button>
								{/each}
							</div>
						</div>
					{/if}
				</div>

				<div class="users-sidebar">
					<h3>Participants ({users.length})</h3>
					<div class="users-list">
						{#each users as user}
							<div class="user-item">
								<div class="user-info">
									<i class="fas fa-user"></i>
									<span>{user.username}</span>
									{#if user.is_host}
										<span class="host-indicator">👑</span>
									{/if}
								</div>
								{#if isHost && !user.is_host}
									<button class="transfer-btn" on:click={() => transferHost(user.user_id)}>
										Transférer hôte
									</button>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			</div>
		</div>
	{/if}

	{#if showAnimeSelector && isHost}
		<div class="modal-overlay" on:click={() => { showAnimeSelector = false; searchQuery = ''; searchResults = []; }}>
			<div class="modal-content" on:click|stopPropagation>
				<h2>Sélection d'anime</h2>

				{#if !selectedAnime}
					<div class="search-input">
						<i class="fas fa-search"></i>
						<input
							type="text"
							placeholder="Rechercher un anime..."
							bind:value={searchQuery}
							on:input={handleSearchInput}
							autofocus
						/>
					</div>

					{#if isSearching}
						<div class="search-loading">
							<i class="fas fa-spinner fa-spin"></i>
						</div>
					{:else if searchResults.length > 0}
						<div class="anime-results">
							{#each searchResults as anime}
								<button class="anime-result-item" on:click={() => selectAnimeFromList(anime)}>
									<img src={anime.img} alt={anime.title} />
									<div class="anime-result-info">
										<span class="anime-title">{anime.title}</span>
										{#if anime.genre && anime.genre.length > 0}
											<span class="anime-genre">{anime.genre[0]}</span>
										{/if}
									</div>
								</button>
							{/each}
						</div>
					{:else if searchQuery.length >= 2}
						<p class="no-results">Aucun résultat pour "{searchQuery}"</p>
					{:else}
						<p class="help-text">Tapez au moins 2 caractères pour rechercher un anime</p>
					{/if}

					<button class="cancel-btn" on:click={() => { showAnimeSelector = false; searchQuery = ''; searchResults = []; }}>
						Annuler
					</button>
				{:else}
					<div class="anime-selected">
						<div class="anime-selected-header">
							<h3>{selectedAnime.title}</h3>
							<button class="back-btn" on:click={() => { selectedAnime = null; searchQuery = ''; searchResults = []; }}>
								<i class="fas fa-arrow-left"></i>
								Retour
							</button>
						</div>

						{#if allSeasons.length > 0}
							<div class="selector-group">
								<label>Saison:</label>
								<select bind:value={selectedSeasonIdx} on:change={changeSeason}>
									{#each allSeasons as season, idx}
										<option value={idx}>{season.name}</option>
									{/each}
								</select>
							</div>

							<div class="selector-group">
								<label>Épisode:</label>
								<select bind:value={selectedEpisode} on:change={updateEpisodeSources}>
									{#each Array(nbEpisodes) as _, idx}
										<option value={idx}>Épisode {idx + 1}</option>
									{/each}
								</select>
							</div>

							<div class="selector-group">
								<label>Source:</label>
								<select bind:value={selectedSource}>
									{#each srcsList as src, idx}
										<option value={idx}>Source {idx + 1}</option>
									{/each}
								</select>
							</div>

							<button class="confirm-btn" on:click={changeSource}>
								Confirmer
							</button>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	#together-container {
		width: 100%;
		height: 100%;
		background-color: #0d0d0d;
		color: #ffffff;
	}

	.lobby {
		max-width: 800px;
		margin: 0 auto;
		padding: 3rem 2rem;
	}

	.lobby h1 {
		font-size: 2.5rem;
		margin-bottom: 0.5rem;
		text-align: center;
	}

	.subtitle {
		text-align: center;
		color: rgba(255, 255, 255, 0.6);
		margin-bottom: 2rem;
	}

	.create-room-btn {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin: 0 auto 3rem;
		padding: 1rem 2rem;
		background: linear-gradient(135deg, #f59e0b, #d97706);
		color: white;
		border: none;
		border-radius: 0.75rem;
		font-size: 1.1rem;
		font-weight: 600;
		cursor: pointer;
		transition: transform 0.2s;
	}

	.create-room-btn:hover {
		transform: translateY(-2px);
	}

	.rooms-list {
		margin-top: 2rem;
	}

	.rooms-list h2 {
		font-size: 1.5rem;
		margin-bottom: 1rem;
	}

	.empty-state {
		text-align: center;
		color: rgba(255, 255, 255, 0.4);
		padding: 2rem;
	}

	.room-card {
		display: flex;
		justify-content: space-between;
		align-items: center;
		background-color: rgba(255, 255, 255, 0.05);
		padding: 1.5rem;
		border-radius: 0.75rem;
		margin-bottom: 1rem;
		transition: background-color 0.2s;
	}

	.room-card:hover {
		background-color: rgba(255, 255, 255, 0.08);
	}

	.room-info h3 {
		font-size: 1.2rem;
		margin-bottom: 0.25rem;
	}

	.room-info p {
		color: rgba(255, 255, 255, 0.5);
		font-size: 0.9rem;
	}

	.join-btn {
		padding: 0.75rem 1.5rem;
		background-color: #f59e0b;
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-weight: 600;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.join-btn:hover {
		background-color: #d97706;
	}

	.room-view {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.room-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem 2rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.room-title {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.room-title h2 {
		font-size: 1.5rem;
	}

	.host-badge {
		background-color: #f59e0b;
		color: white;
		padding: 0.25rem 0.75rem;
		border-radius: 1rem;
		font-size: 0.8rem;
		font-weight: 600;
	}

	.leave-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1.25rem;
		background-color: rgba(239, 68, 68, 0.2);
		color: #ef4444;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.leave-btn:hover {
		background-color: rgba(239, 68, 68, 0.3);
	}

	.room-content {
		display: flex;
		flex: 1;
		overflow: hidden;
	}

	.video-section {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		min-width: 0;
	}

	.video-container {
		position: relative;
		width: 100%;
		flex: 1;
		background-color: #000;
		border-radius: 0.75rem;
		overflow: hidden;
	}

	.video-container.fullscreen {
		position: fixed;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		z-index: 1000;
		border-radius: 0;
	}

	video {
		width: 100%;
		height: 100%;
		object-fit: contain;
		cursor: pointer;
	}

	.loader-overlay, .no-video-overlay {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		color: #fff;
		text-align: center;
		pointer-events: none;
	}

	.loader-overlay i {
		font-size: 3rem;
	}

	.no-video-overlay {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		pointer-events: auto;
	}

	.no-video-overlay i {
		font-size: 4rem;
		opacity: 0.3;
	}

	.no-video-overlay button {
		margin-top: 1rem;
		padding: 0.75rem 1.5rem;
		background-color: #f59e0b;
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-weight: 600;
		cursor: pointer;
	}

	.wait-message {
		color: rgba(255, 255, 255, 0.5);
		font-style: italic;
	}

	.controls-overlay {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
		padding: 1rem;
		opacity: 0;
		transition: opacity 0.2s;
	}

	.controls-overlay.visible {
		opacity: 1;
	}

	.progress-bar {
		height: 4px;
		background-color: rgba(255, 255, 255, 0.3);
		border-radius: 2px;
		cursor: pointer;
		margin-bottom: 0.75rem;
	}

	.progress-bar:hover {
		height: 6px;
	}

	.progress {
		height: 100%;
		background-color: #f59e0b;
		border-radius: 2px;
		transition: width 0.1s linear;
	}

	.controls {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.controls button {
		background: none;
		border: none;
		color: #fff;
		cursor: pointer;
		font-size: 1rem;
		padding: 0.25rem;
		transition: color 0.2s;
	}

	.controls button:hover {
		color: #f59e0b;
	}

	.volume-control {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.volume-control input[type="range"] {
		width: 80px;
		height: 4px;
		-webkit-appearance: none;
		appearance: none;
		background: rgba(255, 255, 255, 0.3);
		border-radius: 2px;
		cursor: pointer;
	}

	.volume-control input[type="range"]::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 12px;
		height: 12px;
		background: #f59e0b;
		border-radius: 50%;
		cursor: pointer;
	}

	.volume-control input[type="range"]::-moz-range-thumb {
		width: 12px;
		height: 12px;
		background: #f59e0b;
		border-radius: 50%;
		cursor: pointer;
		border: none;
	}

	.time {
		font-size: 0.85rem;
		color: rgba(255, 255, 255, 0.8);
	}

	.spacer {
		flex: 1;
	}

	.users-sidebar {
		width: 300px;
		background-color: rgba(255, 255, 255, 0.03);
		border-left: 1px solid rgba(255, 255, 255, 0.1);
		padding: 1.5rem;
		overflow-y: auto;
	}

	.users-sidebar h3 {
		font-size: 1.2rem;
		margin-bottom: 1rem;
	}

	.users-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.user-item {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		padding: 0.75rem;
		background-color: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
	}

	.user-info {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.host-indicator {
		margin-left: auto;
	}

	.transfer-btn {
		padding: 0.5rem;
		background-color: rgba(245, 158, 11, 0.2);
		color: #f59e0b;
		border: none;
		border-radius: 0.375rem;
		font-size: 0.8rem;
		cursor: pointer;
	}

	.transfer-btn:hover {
		background-color: rgba(245, 158, 11, 0.3);
	}

	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.8);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}

	.modal-content {
		background-color: #1a1a1a;
		padding: 2rem;
		border-radius: 1rem;
		max-width: 500px;
		width: 90%;
	}

	.modal-content h2 {
		margin-bottom: 1.5rem;
	}

	.selector-group {
		margin-bottom: 1rem;
	}

	.selector-group label {
		display: block;
		margin-bottom: 0.5rem;
		color: rgba(255, 255, 255, 0.7);
	}

	.selector-group select {
		width: 100%;
		padding: 0.75rem;
		background-color: rgba(255, 255, 255, 0.1);
		color: white;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 0.5rem;
		font-size: 1rem;
	}

	.confirm-btn {
		width: 100%;
		margin-top: 1.5rem;
		padding: 1rem;
		background-color: #f59e0b;
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-weight: 600;
		cursor: pointer;
	}

	.confirm-btn:hover {
		background-color: #d97706;
	}

	.search-input {
		display: flex;
		align-items: center;
		background-color: rgba(255, 255, 255, 0.1);
		border-radius: 0.5rem;
		padding: 0.75rem 1rem;
		margin-bottom: 1.5rem;
	}

	.search-input i {
		color: rgba(255, 255, 255, 0.5);
		margin-right: 0.75rem;
	}

	.search-input input {
		background: none;
		border: none;
		color: white;
		width: 100%;
		font-size: 1rem;
		outline: none;
	}

	.search-input input::placeholder {
		color: rgba(255, 255, 255, 0.4);
	}

	.search-loading {
		text-align: center;
		padding: 2rem;
		color: rgba(255, 255, 255, 0.5);
	}

	.search-loading i {
		font-size: 2rem;
	}

	.anime-results {
		max-height: 400px;
		overflow-y: auto;
		margin-bottom: 1rem;
	}

	.anime-result-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		width: 100%;
		padding: 0.75rem;
		background: none;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: background-color 0.2s;
		text-align: left;
		margin-bottom: 0.5rem;
	}

	.anime-result-item:hover {
		background-color: rgba(255, 255, 255, 0.1);
	}

	.anime-result-item img {
		width: 50px;
		height: 70px;
		object-fit: cover;
		border-radius: 0.375rem;
		flex-shrink: 0;
	}

	.anime-result-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		min-width: 0;
	}

	.anime-title {
		font-size: 1rem;
		font-weight: 500;
		color: white;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.anime-genre {
		font-size: 0.85rem;
		color: rgba(255, 255, 255, 0.5);
	}

	.no-results, .help-text {
		text-align: center;
		color: rgba(255, 255, 255, 0.5);
		padding: 2rem;
	}

	.cancel-btn {
		width: 100%;
		padding: 0.75rem;
		background-color: rgba(255, 255, 255, 0.1);
		color: white;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		margin-top: 1rem;
	}

	.cancel-btn:hover {
		background-color: rgba(255, 255, 255, 0.15);
	}

	.anime-selected-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1.5rem;
	}

	.anime-selected-header h3 {
		margin: 0;
	}

	.back-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background-color: rgba(255, 255, 255, 0.1);
		color: white;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		font-size: 0.9rem;
	}

	.back-btn:hover {
		background-color: rgba(255, 255, 255, 0.15);
	}

	.error-toast {
		position: fixed;
		top: 2rem;
		right: 2rem;
		background-color: #dc2626;
		color: white;
		padding: 1rem 1.5rem;
		border-radius: 0.75rem;
		box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		gap: 1rem;
		z-index: 10000;
		max-width: 400px;
		animation: slideIn 0.3s ease-out;
	}

	@keyframes slideIn {
		from {
			transform: translateX(100%);
			opacity: 0;
		}
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}

	.error-toast i.fa-exclamation-circle {
		font-size: 1.5rem;
		flex-shrink: 0;
	}

	.error-toast span {
		flex: 1;
		font-size: 0.95rem;
	}

	.close-error {
		background: none;
		border: none;
		color: white;
		cursor: pointer;
		padding: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		opacity: 0.8;
		transition: opacity 0.2s;
		flex-shrink: 0;
	}

	.close-error:hover {
		opacity: 1;
	}

	.watching-section {
		margin-top: 1rem;
	}

	.watching-section h3 {
		font-size: 1rem;
		margin-bottom: 0.75rem;
		color: rgba(255, 255, 255, 0.8);
	}

	.watching-list {
		display: flex;
		gap: 0.75rem;
		overflow-x: auto;
		padding-bottom: 0.5rem;
	}

	.watching-list::-webkit-scrollbar {
		height: 6px;
	}

	.watching-list::-webkit-scrollbar-track {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 3px;
	}

	.watching-list::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.3);
		border-radius: 3px;
	}

	.watching-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
		background: rgba(255, 255, 255, 0.05);
		border: none;
		border-radius: 0.5rem;
		padding: 0.5rem;
		cursor: pointer;
		transition: background-color 0.2s, transform 0.2s;
		flex-shrink: 0;
		width: 100px;
	}

	.watching-item:hover {
		background: rgba(255, 255, 255, 0.1);
		transform: translateY(-2px);
	}

	.watching-item img {
		width: 80px;
		height: 110px;
		object-fit: cover;
		border-radius: 0.375rem;
	}

	.watching-info {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.25rem;
		width: 100%;
	}

	.watching-title {
		font-size: 0.75rem;
		color: white;
		text-align: center;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		width: 100%;
	}

	.watching-episode {
		font-size: 0.7rem;
		color: #f59e0b;
		font-weight: 600;
	}
</style>
