<script lang='ts'>
	import '@fortawesome/fontawesome-free/css/all.css';
	import { onMount } from 'svelte';
	import Loader from '../Global/Loader.svelte';

	export let src: any;
	export let menu: any;

	let video: any				= null;
	let paused: boolean			= true;
	let volume: number			= 0.75;
	let currentTime: number		= 0;
	let duration: number		= 0;
	let fullscreen: boolean		= false;
	let buffering: boolean		= false;

	menu.dominantColor = '#c7c7c75c';
	onMount(() => {
		video = document.querySelector('video');
		src.subscribe((value: string) => {
			putSrc(value);
		});
	});

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
		if (sourceVideo == '' || sourceVideo == undefined)
				return;
		if (sourceVideo.includes('.m3u8'))
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
		{
			video?.setAttribute('src', sourceVideo);
			console.log(video?.getAttribute('src'));
		}
	}
</script>

<main id="player-container">
	<div style="background-color: #000; overflow: scroll; border-radius: 0.5rem 0.5rem 0 0; position: relative;">
		<div style="max-width: 80rem; margin: 0 auto;">
			<div id="player">
				<!-- svelte-ignore a11y_media_has_caption -->
				<video
					on:pause={() => paused = true}
					on:play={() => paused = false}
					on:loadedmetadata={() => {
						duration = video.duration;
					}}
					on:timeupdate={() => {
						const bar = document.querySelector('.progress') as HTMLElement;
						if (bar)
							bar.style.width = (video.currentTime / duration) * 100 + '%';
						currentTime = video.currentTime;
					}}
					on:waiting={() => buffering = true}
					on:playing={() => buffering = false}
				>
				</video>
			</div>
		</div>
		{#if buffering}
			<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 999;">
				<Loader scale={2} />
			</div>
		{/if}
		<div id="overlay">
			<div class="bottom">
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<!-- svelte-ignore a11y_click_events_have_key_events -->
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
					<i class="fas fa-volume-up volume"></i>
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<div class="input-range" on:click={(event) => {
						const bar = document.querySelector('.input-range') as HTMLElement;
						const width = bar.offsetWidth;
						const x = event.clientX - bar.getBoundingClientRect().left;
						let percent = x / width;
						if (percent < 0)
							percent = 0;
						else if (percent > 100)
							percent = 100;
						volume = percent;
						video.volume = percent;
						
					}}>
						<div class="progress" style="width: {volume * 100}%"></div>
					</div>
					<span style="margin-inline: 1rem">{secondsToHms(currentTime)} / {secondsToHms(duration)}</span>
					<div style="margin: auto;"></div>
					<!-- svelte-ignore a11y_consider_explicit_label -->
					<button class="no-style-button">
						<i style="margin-left: 1rem; color: white" class="fas fa-gear"></i>
					</button>
					<!-- svelte-ignore a11y_consider_explicit_label -->
					<button class="no-style-button" on:click={() => {
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
							<i style="margin-left: 1rem; color: white" class="fas fa-compress"></i>
						{:else}
							<i style="margin-left: 1rem; color: white" class="fas fa-expand"></i>
						{/if}
					</button>
				</div>
			</div>
		</div>
	</div>
</main>

<style>
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
	#overlay {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
	}
	#overlay .bottom {
		position: absolute;
		bottom: 0;
		left: 0;
		width: 100%;
		height: 3rem;
		background: linear-gradient(0deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 100%);
	}
	#overlay .bottom .progress-bar {
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
	#overlay .under-progress {
		width: 93%;
		height: 2.5rem;
		border-radius: 0.5rem;
		display: flex;
		align-items: center;
		margin-inline: auto;
		flex-direction: row;
	}
	.volume {
		margin-left: 1rem;
		margin-right: 0.5rem;
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
</style>