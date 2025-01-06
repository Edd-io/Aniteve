<script lang='ts'>
	import '@fortawesome/fontawesome-free/css/all.css';
	import { onDestroy } from 'svelte';
	import { onMount } from 'svelte';
	import Loader from '../Global/Loader.svelte';

	export let srcs: any;
	export let menu: any;
	export let selectedEpisode: number;
	export let idSelectedSeason: number;
	export let allSeasons: any;
	export let progress: any;

	const	serverUrl					= 'http://localhost:8080';

	let srcsList: string[]				= [];
	let	selectedSource: number			= 0;
	let video: any						= null;
	let paused: boolean					= true;
	let volume: number					= 0.75;
	let currentTime: number				= 0;
	let lastCurrentTime: number			= 0;
	let duration: number				= 0;
	let fullscreen: boolean				= false;
	let buffering: boolean				= false;
	let muted: boolean					= false;
	let showTimerOnProgress: boolean	= false;
	let resolution: string				= '';
	let showSettings: boolean			= false;
	let showSourceSettings: boolean		= false;
	let animationSettings: boolean		= false;
	let timeoutSettings: any			= null;
	let timeoutOverlay: any				= null;
	let animationOverlay: boolean		= false;
	let showOverlay: boolean			= false;
	let hasAlreadyPlayed: boolean		= false;
	let deadSource: boolean				= false;

	menu.dominantColor = '#c7c7c75c';
	onMount(() => {
		video = document.querySelector('video');
		srcs.subscribe((value: any) => {
			srcsList = value;
			resetVariables();
		});
		document.addEventListener("keydown", handleKeydown);
		document.addEventListener('fullscreenchange', handleFullscreen);
		const interval = setInterval(() => {
			fetch(serverUrl + "/api/update_progress", {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					id: menu.data.anime.id,
					episode: selectedEpisode + 1,
					totalEpisode: srcsList.length,
					seasonId: idSelectedSeason,
					allSeasons: allSeasons,
					progress: currentTime * 100 / duration,
					poster: menu.data.tmdb.poster ? menu.data.tmdb.poster : menu.data.anime.img,
				})
			})
		}, 10000);
		return (() => {
			clearInterval(interval);
			window.removeEventListener("keydown", handleKeydown);
			document.removeEventListener('fullscreenchange', handleFullscreen);
		});
	});

	onDestroy(() => {
		video.pause();
		video.removeAttribute('src');
		video.load();
		document.removeEventListener("keydown", handleKeydown);
		document.removeEventListener('fullscreenchange', handleFullscreen);
	});

	function resetVariables()
	{
		hasAlreadyPlayed = false;
		selectedSource = 0;
		currentTime = 0;
		lastCurrentTime = 0;
		duration = 0;
		buffering = false;
		muted = false;
		showTimerOnProgress = false;
		resolution = '';
		showSettings = false;
		showSourceSettings = false;
		animationSettings = false;
		animationOverlay = false;
		showOverlay = false;
		changeSource();
	}

	function handleFullscreen()
	{
		if (!document.fullscreenElement)
			fullscreen = false;
		else
			fullscreen = true;
	}

	function handleKeydown(event: any)
	{
		const bar = document.querySelector('.progress') as HTMLElement;

		if (event.key == ' ')
		{
			event.preventDefault();
			if (video.paused)
				video.play();
			else
				video.pause();
		}
		else if (event.key == 'ArrowRight')
		{
			video.currentTime += 15;
			if (bar)
				bar.style.width = (video.currentTime / duration) * 100 + '%';
		}
		else if (event.key == 'ArrowLeft')
		{
			video.currentTime -= 15;
			if (bar)
				bar.style.width = (video.currentTime / duration) * 100 + '%';
		}
		else if (event.key == 'ArrowUp')
		{
			if (video.volume + 0.1 > 1)
				video.volume = 1;
			else
				video.volume += 0.1;
		}
		else if (event.key == 'ArrowDown')
		{
			if (video.volume - 0.1 < 0)
				video.volume = 0;
			else
				video.volume -= 0.1;
		}
	}

	function secondsToHms(d: number)
	{
		d = Number(d);
		const h = Math.floor(d / 3600);
		const m = Math.floor(d % 3600 / 60);
		const s = Math.floor(d % 3600 % 60);

		const hDisplay = h > 0 ? (h < 10 ? '0' + h : h) + ':' : '';
		const mDisplay = m > 0 ? (m < 10 ? '0' + m : m) + ':' : '00:';
		const sDisplay = s > 0 ? (s < 10 ? '0' + s : s) : '00';
		return (hDisplay + mDisplay + sDisplay);
	};

	function putSrc(sourceVideo: string)
	{
		if (sourceVideo && sourceVideo.includes('.m3u8'))
		{
			if (video?.canPlayType('application/vnd.apple.mpegurl'))
				video?.setAttribute('src', sourceVideo);
			else
			{
				const script = document.createElement('script');
				script.src = "https://cdn.jsdelivr.net/npm/hls.js@latest";
				script.onload = () => {
					if (Hls.isSupported())
					{
						const hls = new Hls();
						hls.loadSource(sourceVideo);
						hls.attachMedia(video);
					}
					else
						alert("Votre navigateur ne supporte pas la lecture HLS.");
				};
				document.body.appendChild(script);
			}
		}
		else
			video?.setAttribute('src', sourceVideo);
		if (sourceVideo === null)
			deadSource = true;
	}

	function changeSource()
	{
		if (srcsList.length == 0)
			return;
		deadSource = false;
		fetch(srcsList[selectedSource], {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({serverUrl: serverUrl}),
		}).then((response) => {
			return response.json();
		}).then((data) => {
			putSrc(data.src);
		}).catch((error) => {
			console.error(error);
		});
		if (progress.find)
		{
			hasAlreadyPlayed = true;
			buffering = true;
		}
	}

	function addNewDownload()
	{
		menu.downloader.addNewDownload({
			poster: menu.data.tmdb.poster ? menu.data.tmdb.poster : menu.data.anime.img,
			episode: selectedEpisode + 1,
			season: allSeasons[idSelectedSeason],
			src: video.src,
			title: menu.data.anime.title,
		});
	}
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<main id="player-container"
	on:mousemove={() => {
		const bar = document.querySelector('.progress') as HTMLElement;

		if (!hasAlreadyPlayed)
			return;
		if (bar)
			bar.style.width = (video.currentTime / duration) * 100 + '%';
		if (timeoutOverlay)
			clearTimeout(timeoutOverlay);
		animationOverlay = true;
		showOverlay = true;
		timeoutOverlay = setTimeout(() => {
			animationOverlay = false;
			timeoutOverlay = setTimeout(() => {
				showOverlay = false;
			}, 200);
		}, 2000);
	}}
	on:dblclick={() => {
		if (document.fullscreenElement)
		{
			document.exitFullscreen();
			fullscreen = false;
		}
		else
		{
			document.querySelector('#player-container')?.requestFullscreen();
			fullscreen = true;
		}
	}}
>
	<div style="background-color: #000; overflow: scroll; border-radius: 0.5rem 0.5rem 0 0; position: relative; {fullscreen ? 'height: 100%;' : ''}">
		<div style="{fullscreen ? "width: 100%; heigth: 100%;" : "max-width: 80rem"}; margin: 0 auto;">
			<div id="player" style="{fullscreen ? 'height: 100vh; padding: 0' : ''}">
				{#if !hasAlreadyPlayed}
					<!-- svelte-ignore a11y_consider_explicit_label -->
					<button class="no-style-button" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 999;" on:click={() => video.play()}>
						<i class="fas fa-play" style="font-size: 5rem;"></i>
					</button>
				{/if}
				<!-- svelte-ignore a11y_media_has_caption -->
				<video
					on:pause={() => paused = true}
					on:play={() => {paused = false, hasAlreadyPlayed = true}}
					on:loadedmetadata={() => {
						duration = video.duration;
						resolution = video.videoWidth + 'x' + video.videoHeight;
						if (progress.find)
						{
							video.currentTime = progress.progress * duration / 100;
							progress.find = false;
							hasAlreadyPlayed = true;
						}
					}}
					on:timeupdate={() => {
						const bar = document.querySelector('.progress') as HTMLElement;
						if (bar)
							bar.style.width = (video.currentTime / duration) * 100 + '%';
						currentTime = video.currentTime;
						if (currentTime != 0)
							lastCurrentTime = currentTime;
					}}
					on:loadstart={() => {
						if (hasAlreadyPlayed)
						{
							video.play();
							video.currentTime = lastCurrentTime;
						}
						else
							video.currentTime = 0;
					}}
					on:loadeddata={() => buffering = false}
					on:waiting={() => buffering = true}
					on:playing={() => buffering = false}
					on:click={() => {
						if (video.paused)
							video.play();
						else
							video.pause();
					}}
					preload="auto"
				>
				</video>
			</div>
		</div>
		{#if buffering && !deadSource}
			<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 999;">
				<Loader scale={2} />
			</div>
		{:else if deadSource}
			<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 999;">
				<p style="color: #fff;">Source morte, veuillez en choisir une autre</p>
			</div>
		{/if}
		{#if showOverlay}
			<div class="bottom {animationOverlay ? 'show-animeation-overlay' : 'hide-animeation-overlay'}">
				{#if showSettings}
					<div id="settings" style="height: {showSourceSettings ? '10rem' : '8rem'};" class="{animationSettings ? "show-animation" : "hide-animation"}">
						{#if showSourceSettings}
							<button class="line no-style-button" on:click={() => showSourceSettings = false}>
								<i class="fas fa-arrow-left"></i>
								<p>Retour</p>
								<div style="margin: auto;"></div>
							</button>
							{#if srcsList.length > 0}
								<button class="line no-style-button {selectedSource == 0 ? 'disabled-button' : ''}" on:click={() => selectedSource == 0 ? null : (selectedSource = 0, changeSource())}>
									<p>Source 1</p>
								</button>
							{/if}
							{#if srcsList.length > 1}
							<button class="line no-style-button {selectedSource == 1 ? 'disabled-button' : ''}" on:click={() => selectedSource == 1 ? null : (selectedSource = 1, changeSource())}>
								<p>Source 2</p>
							</button>
							{/if}
							{#if srcsList.length > 2}
							<button class="line no-style-button {selectedSource == 2 ? 'disabled-button' : ''}" on:click={() => selectedSource == 2 ? null : (selectedSource = 2, changeSource())}>
								<p>Source 3</p>
							</button>
							{/if}
							{#if srcsList.length > 3}
							<button class="line no-style-button {selectedSource == 3 ? 'disabled-button' : ''}" on:click={() => selectedSource == 3 ? null : (selectedSource = 3, changeSource())}>
								<p>Source 4</p>
							</button>
							{/if}
						{:else}
							<div class="line" style="color: #eee;">
								<p style="margin: 0;">Résolution</p>
								<div style="margin: auto;"></div>
								<p style="margin: 0;">{resolution}</p>
							</div>
							<button class="line no-style-button" on:click={() => showSourceSettings = true}>
								<i class="fas fa-file-video"></i>
								<p>Source {selectedSource + 1}</p>
								<div style="margin: auto;"></div>
								<i class="fas fa-arrow-right" style='font-size: 0.8rem;'></i>
							</button>
							<button class="line no-style-button" on:click={() => {
								confirm('Voulez-vous vraiment télécharger cet épisode ?') ? addNewDownload() : null;
							}}>
								<i class="fa-solid fa-file-arrow-down"></i>
								<p>Télécharger</p>
								<div style="margin: auto;"></div>
								<i class="fas fa-arrow-right" style='font-size: 0.8rem;'></i>
							</button>
						{/if}
					</div>
				{/if}
				<div id="timer" style="position: absolute; top: -2rem; left: 0; display: {showTimerOnProgress ? 'block' : 'none'}; background-color: #000; color: #fff; padding: 0.2rem; border-radius: 0.5rem;"></div>
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<!-- svelte-ignore a11y_click_events_have_key_events -->
				<!-- svelte-ignore a11y_mouse_events_have_key_events -->
				<div class="progress-bar"
					on:click={(event) => {
						const bar = document.querySelector('.progress-bar') as HTMLElement;
						const progress = document.querySelector('.progress') as HTMLElement;
						const width = bar.offsetWidth;
						const x = event.clientX - bar.getBoundingClientRect().left;
						const percent = x / width;
						progress.style.width = percent * 100 + '%';
						video.currentTime = percent * duration;
					}}
					on:mouseover={() => {
						showTimerOnProgress = true;
					}}
					on:mouseout={() => {
						showTimerOnProgress = false;
					}}
					on:mousemove={(event) => {
						const	timer	= document.querySelector('#timer') as HTMLElement;
						const	bar		= document.querySelector('.progress-bar') as HTMLElement;
						const	x = event.clientX - bar.getBoundingClientRect().left;
						const	percent = x / bar.offsetWidth * 100;

						timer.style.left = (percent * bar.offsetWidth / 100) + 'px';
						timer.innerText = secondsToHms(percent * duration / 100);
					}}
				>
					<div class="progress"></div>
				</div>
				<div class="under-progress">
					<button class="no-style-button" on:click={() => {
						if (video.paused)
							video.play();
						else
							video.pause();
					}}>
						{#if paused}
							<i class="fas fa-play"></i>
						{:else}
							<i class="fas fa-pause"></i>
						{/if}
					</button>
					<!-- svelte-ignore a11y_consider_explicit_label -->
					<button class="no-style-button" style="margin-left: 1rem; margin-right: 0.5rem;" on:click={() => {
						if (video.muted)
						{
							video.muted = false;
							muted = false;
							volume = video.volume;
						}
						else
						{
							video.muted = true;
							muted = true;
							volume = 0;
						}
					}}>
						{#if muted}
							<i class="fas fa-volume-mute"></i>
						{:else}
							<i class="fas fa-volume-up"></i>
						{/if}
					</button>
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<div class="input-range" on:click={(event) => {
						const bar = document.querySelector('.input-range') as HTMLElement;
						const width = bar.offsetWidth;
						const x = event.clientX - bar.getBoundingClientRect().left;
						let percent = x / width;
						muted = false;
						if (percent < 0)
							percent = 0;
						else if (percent > 100)
							percent = 100;
						volume = percent;
						video.volume = percent;
						
					}}>
						<div class="progress" style="width: {volume * 100}%"></div>
					</div>
					<span style="margin-inline: 1rem; font-size: 0.8rem;">{secondsToHms(currentTime)} / {secondsToHms(duration)}</span>
					<div style="margin: auto;"></div>
					<!-- svelte-ignore a11y_consider_explicit_label -->
					<button class="no-style-button" style="margin-left: 1rem;" on:click={(event) => {
						event.stopPropagation();
						if (!showSettings)
						{
							showSettings = true;
							animationSettings = true;
						}
						else
						{
							animationSettings = false;
							timeoutSettings = setTimeout(() => {
								showSettings = false;
							}, 200);
						}
					}}>
						<i class="fas fa-gear"></i>
					</button>
					<!-- svelte-ignore a11y_consider_explicit_label -->
					<button class="no-style-button"  style="margin-left: 1rem;" on:click={() => {
						if (document.fullscreenElement)
						{
							document.exitFullscreen();
							fullscreen = false;
						}
						else
						{
							document.querySelector('#player-container')?.requestFullscreen();
							fullscreen = true;
						}
					}}>
						{#if fullscreen}
							<i class="fas fa-compress"></i>
						{:else}
							<i class="fas fa-expand"></i>
						{/if}
					</button>
				</div>
			</div>
		{/if}
	</div>
</main>

<style>
	#player-container {
		user-select: none;
	}
	#player {
		width: 100%;
		height: 0;
		padding-top: 56.25%;
		object-fit: contain;
		background-color: #000;
		position: relative;
	}
	#player video {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		object-fit: contain;
	}
	.bottom {
		position: absolute;
		bottom: 0;
		left: 0;
		width: 100%;
		height: 3rem;
		background: linear-gradient(0deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 100%);
	}
	.bottom .progress-bar {
		width: 95%;
		height: 0.5rem;
		background-color: #ffffff89;
		border-radius: 0.5rem;
		margin-inline: auto;
	}
	.progress {
		width: 0;
		height: 100%;
		background-color: #547ff3;
		border-radius: 0.5rem;
		overflow: hidden;
		pointer-events: 'auto';
	}
	.under-progress {
		width: 93%;
		height: 2.5rem;
		border-radius: 0.5rem;
		display: flex;
		align-items: center;
		margin-inline: auto;
		flex-direction: row;
	}
	.input-range {
		width: 5rem;
		background: #ddd;
		border-radius: 0.5rem;
		height: 0.5rem;
	}
	.no-style-button {
		background-color: transparent;
		border: none;
		cursor: pointer;
		display: flex;
		align-items: center;
		color: #fff;
	}
	.no-style-button:hover {
		color: #547ff3;
	}
	#settings {
		position: absolute;
		display: flex;
		background-color: #b5b5b589;
		width: 15rem;
		right: 2.5%;
		border-radius: 0.5rem;
		transform: translateY(calc(-100% - 0.3rem));
		box-shadow: 0 0 100px #00000077;
		padding: 0.8rem;
		flex-direction: column;
		transition: height 0.3s ease-out;
	}
	.show-animation {
		animation: animationShowSettings 0.5s;
	}
	.hide-animation {
		animation: animationHideSettings 0.5s;
	}
	#settings .line {
		width: 100%;
		height: 2rem;
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
	}
	#settings .line p {
		font-size: 0.9rem;
		margin-inline: 0.5rem;
	}
	#settings button i {
		font-size: 1.5rem;
	}
	.show-animeation-overlay {
		animation: animationShowOverlay 0.5s;
	}
	.hide-animeation-overlay {
		animation: animationHideOverlay 0.5s;
	}
	.disabled-button {
		background-color: #0000003b;
	}
	@keyframes animationShowSettings {
		from {
			right: 0;
			opacity: 0;
			transform: translate(100%, calc(-100% - 0.3rem));
		}
		to {
			right: 2.5%;
			opacity: 1;
			transform: translateY(0, calc(-100% - 0.3rem));
		}
	}
	@keyframes animationHideSettings {
		from {
			right: 2.5%;
			opacity: 1;
			transform: translateY(0, calc(-100% - 0.3rem));
		}
		to {
			right: 0;
			opacity: 0;
			transform: translate(100%, calc(-100% - 0.3rem));
		}
	}
	@keyframes animationShowOverlay {
		from {
			transform: translateY(100%);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}
	@keyframes animationHideOverlay {
		from {
			transform: translateY(0);
			opacity: 1;
		}
		to {
			transform: translateY(100%);
			opacity: 0;
		}
	}
	

</style>