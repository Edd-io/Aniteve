<script lang='ts'>
	import '@fortawesome/fontawesome-free/css/all.css';
	import { onMount, onDestroy } from 'svelte';
	import { writable } from "svelte/store";
	import { navigate } from 'svelte-routing';

	export let menu: any;

	const serverUrl = '';
	const anime = menu.data;
	const banGenre = ['vostfr', 'vf', 'cardlistanime', 'anime', '-', 'scans', 'film'];
	const listSource: any = writable([]);

	let allSeasons: any[] = [];
	let genreString: string[] = [];
	let progressData: any = { find: false };
	let isLoading = true;
	let nbEpisodes = 0;
	let listUrlEpisodes: any = [];
	let idSelectedSeason = 0;
	let selectedEpisode = 0;

	let srcsList: string[] = [];
	let selectedSource = 0;
	let video: any = null;
	let paused = true;
	let volume = 0.75;
	let currentTime = 0;
	let lastCurrentTime = 0;
	let duration = 0;
	let fullscreen = false;
	let buffering = false;
	let muted = false;
	let showOverlay = false;
	let animationOverlay = false;
	let hasAlreadyPlayed = false;
	let deadSource = false;
	let src = '';
	let timeoutOverlay: any = null;
	let showSettings = false;
	let tmdbPoster: string | null = null;

	menu.dominantColor = '#0d0d0d';
	menu.selected = 4;

	anime?.genre?.forEach((genre: string) => {
		if (!banGenre.includes(genre.toLowerCase())) {
			const mainGenre = genre.split(' - ')[0].trim();
			if (mainGenre && !genreString.includes(mainGenre)) {
				genreString.push(mainGenre);
			}
		}
	});

	onMount(() => {
		video = document.querySelector('video');
		fetchTmdbPoster();
		fetchSeasons();

		listSource.subscribe((value: any) => {
			srcsList = value;
			if (srcsList.length > 0) {
				resetVideoState();
			}
		});

		document.addEventListener("keydown", handleKeydown);
		document.addEventListener('fullscreenchange', handleFullscreen);

		const progressInterval = setInterval(() => {
			if (!hasAlreadyPlayed || !duration) return;

			const progress = currentTime * 100 / duration;
			fetch(serverUrl + "/api/update_progress", {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': localStorage.getItem('token') || '',
				},
				body: JSON.stringify({
					id: anime.id,
					episode: selectedEpisode + 1,
					totalEpisode: nbEpisodes,
					seasonId: idSelectedSeason,
					allSeasons: allSeasons,
					progress: progress || 0,
					poster: tmdbPoster || anime.img,
					idUser: menu.user.id,
				})
			}).catch(console.error);
		}, 10000);

		return () => {
			clearInterval(progressInterval);
			document.removeEventListener("keydown", handleKeydown);
			document.removeEventListener('fullscreenchange', handleFullscreen);
		};
	});

	onDestroy(() => {
		if (video) {
			video.pause();
			video.removeAttribute('src');
			video.load();
		}
	});

	function fetchTmdbPoster() {
		const searchTitle = anime.title.replace(/\s+saison\s+\d+/i, '').trim();
		const tmdbSearchUrl = `https://api.themoviedb.org/3/search/tv?{api_key_tmdb}&query=${encodeURIComponent(searchTitle)}&language=fr-FR`;

		fetch(serverUrl + '/api/tmdb', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({ url: tmdbSearchUrl }),
		})
		.then(res => res.json())
		.then(data => {
			if (data.results && data.results.length > 0) {
				const posterPath = data.results[0].poster_path;
				if (posterPath) {
					tmdbPoster = `https://image.tmdb.org/t/p/w500${posterPath}`;
				}
			}
		})
		.catch(err => console.error('TMDB fetch error:', err));
	}

	function fetchSeasons() {
		fetch(serverUrl + '/api/get_anime_season', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({ url: anime.url, serverUrl: serverUrl }),
		})
		.then(res => res.json())
		.then(data => {
			allSeasons = data.season || [];

			if (anime?.genre?.some((g: string) => g.toLowerCase() === 'vf')) {
				const vfSeasons = allSeasons.map(s => ({
					...s,
					url: s.url.replace('vostfr', 'vf'),
					lang: 'vf'
				}));
				allSeasons = [...allSeasons, ...vfSeasons];
			}

			fetchProgress();
		})
		.catch(err => {
			console.error(err);
			isLoading = false;
		});
	}

	function fetchProgress() {
		fetch(serverUrl + '/api/get_progress', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({ id: anime.id, idUser: menu.user.id }),
		})
		.then(res => res.json())
		.then(data => {
			progressData = data;

			if (data.find && allSeasons.length > 0) {
				selectedEpisode = data.episode - 1;
				idSelectedSeason = allSeasons.findIndex(s => s.url === data.season);
				if (idSelectedSeason === -1) idSelectedSeason = 0;
			}

			changeSeason();
			isLoading = false;
		})
		.catch(err => {
			console.error(err);
			changeSeason();
			isLoading = false;
		});
	}

	function changeSeason() {
		if (!allSeasons.length) return;

		fetch(serverUrl + '/api/get_anime_episodes', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({
				url: anime.url,
				season: allSeasons[idSelectedSeason].url,
				serverUrl: window.location.origin
			}),
		})
		.then(res => res.json())
		.then(data => {
			nbEpisodes = data.number || 0;
			listUrlEpisodes = data.episodes || [];
			changeEpisode();
		})
		.catch(() => {
			nbEpisodes = 0;
			listUrlEpisodes = [];
		});
	}

	function changeEpisode() {
		listSource.update(() => listUrlEpisodes['eps' + (selectedEpisode + 1)] || []);
	}

	function resetVideoState() {
		hasAlreadyPlayed = false;
		selectedSource = 0;
		currentTime = 0;
		lastCurrentTime = 0;
		duration = 0;
		buffering = false;
		deadSource = false;
		changeSource();
	}

	function changeSource() {
		if (srcsList.length === 0) return;
		deadSource = false;

		fetch(srcsList[selectedSource], {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({ serverUrl: window.location.origin }),
		})
		.then(res => res.json())
		.then(data => {
			src = data.src;
			putSrc(data.src);
		})
		.catch(console.error);

		if (progressData.find) {
			hasAlreadyPlayed = true;
			buffering = true;
		}
	}

	function putSrc(sourceVideo: string) {
		if (!sourceVideo) {
			deadSource = true;
			return;
		}

		if (sourceVideo.includes('.m3u8')) {
			if (video?.canPlayType('application/vnd.apple.mpegurl')) {
				video?.setAttribute('src', sourceVideo);
			} else {
				const script = document.createElement('script');
				script.src = "https://cdn.jsdelivr.net/npm/hls.js@latest";
				script.onload = () => {
					if (Hls.isSupported()) {
						const hls = new Hls();
						hls.loadSource(sourceVideo);
						hls.attachMedia(video);
					}
				};
				document.body.appendChild(script);
			}
		} else {
			video?.setAttribute('src', sourceVideo);
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === ' ') {
			event.preventDefault();
			video?.paused ? video.play() : video.pause();
		} else if (event.key === 'ArrowRight') {
			if (video) video.currentTime += 10;
		} else if (event.key === 'ArrowLeft') {
			if (video) video.currentTime -= 10;
		} else if (event.key === 'ArrowUp') {
			if (video) video.volume = Math.min(1, video.volume + 0.1);
		} else if (event.key === 'ArrowDown') {
			if (video) video.volume = Math.max(0, video.volume - 0.1);
		} else if (event.key === 'f') {
			toggleFullscreen();
		}
	}

	function handleFullscreen() {
		fullscreen = !!document.fullscreenElement;
	}

	function toggleFullscreen() {
		if (document.fullscreenElement) {
			document.exitFullscreen();
		} else {
			document.querySelector('#player-container')?.requestFullscreen();
		}
	}

	function secondsToHms(d: number): string {
		const h = Math.floor(d / 3600);
		const m = Math.floor(d % 3600 / 60);
		const s = Math.floor(d % 60);
		return (h > 0 ? `${h}:` : '') + `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
	}

	function handleMouseMove() {
		if (!hasAlreadyPlayed) return;

		if (timeoutOverlay) clearTimeout(timeoutOverlay);
		animationOverlay = true;
		showOverlay = true;

		timeoutOverlay = setTimeout(() => {
			animationOverlay = false;
			setTimeout(() => showOverlay = false, 200);
		}, 3000);
	}

	function handleProgressClick(event: MouseEvent) {
		const bar = event.currentTarget as HTMLElement;
		const percent = (event.clientX - bar.getBoundingClientRect().left) / bar.offsetWidth;
		if (video) video.currentTime = percent * duration;
	}

	function selectEpisode(index: number) {
		selectedEpisode = index;
		changeEpisode();
	}

	function addDownload() {
		if (!confirm('Télécharger cet épisode ?')) return;

		fetch(serverUrl + "/api/download", {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({
				src: src,
				name: anime.title,
				episode: selectedEpisode + 1,
				season: allSeasons[idSelectedSeason],
				serverUrl: window.location.origin,
				poster: tmdbPoster || anime.img,
			})
		})
		.then(() => alert('Téléchargement lancé'))
		.catch(console.error);
	}
</script>

<main>
	{#if isLoading}
		<div class="loading">
			<i class="fas fa-spinner fa-spin"></i>
		</div>
	{:else}
		<div class="player-layout">
			<!-- Video Player -->
			<div class="video-section">
				<div
					id="player-container"
					class:fullscreen
					on:mousemove={handleMouseMove}
					on:dblclick={toggleFullscreen}
				>
					<video
						bind:this={video}
						on:pause={() => paused = true}
						on:play={() => { paused = false; hasAlreadyPlayed = true; }}
						on:loadedmetadata={() => {
							if (!video) return;
							duration = video.duration;
							if (progressData.find) {
								video.currentTime = progressData.progress * duration / 100;
								progressData.find = false;
							}
						}}
						on:timeupdate={() => {
							if (!video) return;
							currentTime = video.currentTime;
							if (currentTime > 0) lastCurrentTime = currentTime;
						}}
						on:loadstart={() => {
							if (!video) return;
							if (hasAlreadyPlayed) {
								video.play();
								video.currentTime = lastCurrentTime;
							}
						}}
						on:loadeddata={() => buffering = false}
						on:waiting={() => buffering = true}
						on:playing={() => buffering = false}
						on:click={() => video?.paused ? video.play() : video.pause()}
						on:error={() => deadSource = true}
						preload="auto"
					></video>

					{#if !hasAlreadyPlayed && !deadSource}
						<button class="play-button" on:click={() => video?.play()}>
							<i class="fas fa-play"></i>
						</button>
					{/if}

					{#if buffering && !deadSource}
						<div class="loader-overlay">
							<i class="fas fa-spinner fa-spin"></i>
						</div>
					{/if}

					{#if deadSource}
						<div class="error-overlay">
							<i class="fas fa-exclamation-triangle"></i>
							<p>Source indisponible</p>
							{#if srcsList.length > 1}
								<button on:click={() => { selectedSource = (selectedSource + 1) % srcsList.length; changeSource(); }}>
									Essayer une autre source
								</button>
							{/if}
						</div>
					{/if}

					{#if showOverlay}
						<div class="controls-overlay" class:visible={animationOverlay}>
							<div class="progress-bar" on:click={handleProgressClick}>
								<div class="progress" style="width: {(currentTime / duration) * 100}%"></div>
							</div>
							<div class="controls">
								<button on:click={() => video?.paused ? video.play() : video.pause()}>
									<i class="fas {paused ? 'fa-play' : 'fa-pause'}"></i>
								</button>
								<button on:click={() => { muted = !muted; if (video) video.muted = muted; }}>
									<i class="fas {muted ? 'fa-volume-mute' : 'fa-volume-up'}"></i>
								</button>
								<span class="time">{secondsToHms(currentTime)} / {secondsToHms(duration)}</span>
								<div class="spacer"></div>
								<div class="source-select">
									<button on:click={() => showSettings = !showSettings}>
										<i class="fas fa-cog"></i>
									</button>
									{#if showSettings}
										<div class="settings-dropdown">
											<p class="settings-title">Sources</p>
											{#each srcsList as _, i}
												<button
													class:active={selectedSource === i}
													on:click={() => { selectedSource = i; changeSource(); showSettings = false; }}
												>
													Source {i + 1}
												</button>
											{/each}
											<p class="settings-title">Actions</p>
											<button on:click={addDownload}>
												<i class="fas fa-download"></i> Télécharger
											</button>
										</div>
									{/if}
								</div>
								<button on:click={toggleFullscreen}>
									<i class="fas {fullscreen ? 'fa-compress' : 'fa-expand'}"></i>
								</button>
							</div>
						</div>
					{/if}
				</div>

				<!-- Anime Info -->
				<div class="anime-info">
					<h1>{anime.title}</h1>
					{#if genreString.length > 0}
						<div class="genres">
							{#each genreString.slice(0, 4) as genre}
								<span class="genre-tag">{genre}</span>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<!-- Episode Sidebar -->
			<div class="sidebar">
				<div class="season-selector">
					<select bind:value={idSelectedSeason} on:change={() => { selectedEpisode = 0; changeSeason(); }}>
						{#each allSeasons as season, i}
							<option value={i}>{season.name} ({season.lang.toUpperCase()})</option>
						{/each}
					</select>
				</div>

				<div class="episodes-list">
					{#if nbEpisodes > 0}
						{#each Array(nbEpisodes) as _, i}
							<button
								class="episode-btn"
								class:active={selectedEpisode === i}
								on:click={() => selectEpisode(i)}
							>
								<span class="ep-number">EP {i + 1}</span>
								{#if selectedEpisode === i}
									<i class="fas fa-play"></i>
								{/if}
							</button>
						{/each}
					{:else}
						<p class="no-episodes">Aucun épisode disponible</p>
					{/if}
				</div>
			</div>
		</div>
	{/if}
</main>

<style>
	main {
		flex: 1;
		height: 100%;
		overflow: hidden;
		background-color: #0d0d0d;
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		font-size: 2rem;
		color: rgba(255, 255, 255, 0.5);
	}

	.player-layout {
		display: flex;
		height: 100%;
		gap: 1rem;
		padding: 1rem;
	}

	.video-section {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-width: 0;
	}

	#player-container {
		position: relative;
		width: 100%;
		aspect-ratio: 16 / 9;
		background-color: #000;
		border-radius: 0.75rem;
		overflow: hidden;
	}

	#player-container.fullscreen {
		position: fixed;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		z-index: 1000;
		border-radius: 0;
		aspect-ratio: auto;
	}

	video {
		width: 100%;
		height: 100%;
		object-fit: contain;
	}

	.play-button {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 80px;
		height: 80px;
		border-radius: 50%;
		background-color: rgba(255, 255, 255, 0.2);
		border: none;
		color: #fff;
		font-size: 2rem;
		cursor: pointer;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.play-button:hover {
		background-color: rgba(255, 255, 255, 0.3);
		transform: translate(-50%, -50%) scale(1.1);
	}

	.play-button i {
		margin-left: 5px;
	}

	.loader-overlay, .error-overlay {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		color: #fff;
		text-align: center;
	}

	.loader-overlay i {
		font-size: 3rem;
	}

	.error-overlay i {
		font-size: 3rem;
		color: #f59e0b;
		margin-bottom: 1rem;
	}

	.error-overlay p {
		margin-bottom: 1rem;
	}

	.error-overlay button {
		background-color: rgba(255, 255, 255, 0.1);
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 0.5rem;
		color: #fff;
		cursor: pointer;
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

	.time {
		font-size: 0.85rem;
		color: rgba(255, 255, 255, 0.8);
	}

	.spacer {
		flex: 1;
	}

	.source-select {
		position: relative;
	}

	.settings-dropdown {
		position: absolute;
		bottom: 100%;
		right: 0;
		margin-bottom: 0.5rem;
		background-color: #1a1a1a;
		border-radius: 0.5rem;
		padding: 0.5rem;
		min-width: 150px;
		box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
	}

	.settings-title {
		font-size: 0.7rem;
		color: rgba(255, 255, 255, 0.5);
		padding: 0.25rem 0.5rem;
		margin: 0;
	}

	.settings-dropdown button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.5rem;
		text-align: left;
		font-size: 0.85rem;
		border-radius: 0.25rem;
	}

	.settings-dropdown button.active {
		background-color: rgba(245, 158, 11, 0.2);
		color: #f59e0b;
	}

	.settings-dropdown button:hover {
		background-color: rgba(255, 255, 255, 0.1);
	}

	.anime-info {
		padding: 1rem 0;
	}

	.anime-info h1 {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: #fff;
	}

	.genres {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.genre-tag {
		font-size: 0.75rem;
		padding: 0.25rem 0.75rem;
		background-color: rgba(255, 255, 255, 0.1);
		border-radius: 1rem;
		color: rgba(255, 255, 255, 0.7);
	}

	.sidebar {
		width: 280px;
		min-width: 280px;
		display: flex;
		flex-direction: column;
		background-color: #1a1a1a;
		border-radius: 0.75rem;
		overflow: hidden;
	}

	.season-selector {
		padding: 1rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.season-selector select {
		width: 100%;
		padding: 0.75rem;
		background-color: rgba(255, 255, 255, 0.05);
		border: none;
		border-radius: 0.5rem;
		color: #fff;
		font-size: 0.9rem;
		cursor: pointer;
		appearance: none;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23ffffff' viewBox='0 0 24 24'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: right 0.75rem center;
		background-size: 1.5rem;
	}

	.season-selector select:focus {
		outline: none;
		background-color: rgba(255, 255, 255, 0.1);
	}

	.episodes-list {
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem;
	}

	.episode-btn {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		padding: 0.875rem 1rem;
		margin-bottom: 0.25rem;
		background: none;
		border: none;
		border-radius: 0.5rem;
		color: rgba(255, 255, 255, 0.7);
		cursor: pointer;
		transition: all 0.2s;
		font-size: 0.9rem;
	}

	.episode-btn:hover {
		background-color: rgba(255, 255, 255, 0.05);
		color: #fff;
	}

	.episode-btn.active {
		background-color: rgba(245, 158, 11, 0.15);
		color: #f59e0b;
	}

	.episode-btn i {
		font-size: 0.75rem;
	}

	.no-episodes {
		text-align: center;
		color: rgba(255, 255, 255, 0.5);
		padding: 2rem 1rem;
		font-size: 0.9rem;
	}

	@media (max-width: 900px) {
		.player-layout {
			flex-direction: column;
		}

		.sidebar {
			width: 100%;
			min-width: auto;
			max-height: 300px;
		}
	}
</style>
