<script lang="ts">
	import Home from './Home/Home.svelte';
	import Anime from './Anime/Anime.svelte';
	import Player from './Player/Player.svelte';

	let menu: any = {
		selected: 4 as number,
		data: {}
	}; // 0: home, 1: resume, 2: settings, 3: anime, 4: player
	
</script>


<main>
	<div id="left-bar" style="{menu.selected === 3 ?
		'border-radius: 0.5rem 0 0 0.5rem; background-color: #444;' 
		:
		'background-color: #c7c7c75c; border: 1px solid #c7c7c72b;box-shadow: 0 0 5px #0000003b'
	}">
		<h1 id="logo">Logo</h1>
		<button on:click={() => menu.selected = 0} class='no-style-button {menu.selected === 0 ? "selected" : ""} space'>
			<img src="../assets/img/home.png" alt="home" />
		</button>
		<button on:click={() => menu.selected = 1} class='no-style-button {menu.selected === 1 ? "selected" : ""} space'>
			<img src="../assets/img/resume.png" alt="resume" />
		</button>
		<button on:click={() => menu.selected = 2} class='no-style-button {menu.selected === 2 ? "selected" : ""} space' style="margin-top: auto;">
			<img src="../assets/img/settings.png" alt="settings" />
		</button>
	</div>
	<div id="content">
		{#if menu.selected === 0}
			<Home bind:menu={menu} />
		<!-- {:else if selectedMenu === 1}
			<Resume />
		{:else if selectedMenu === 2}
			<Settings /> -->
		{:else if menu.selected === 3}
			<Anime bind:menu={menu} />
		{:else if menu.selected === 4}
			<Player bind:menu={menu} />
		{/if}
	</div>
</main>

<style>
	main {
		display: flex;
		height: 100vh;
		width: 100vw;
		padding: 1rem;
		position: relative;
	}
	.no-style-button {
		background-color: transparent;
		border: none;
		cursor: pointer;
		padding: 0.4rem;
		display: flex;
		align-items: center;
	}
	#left-bar {
		width: 80px;
		height: 100%;
		border-radius: 0.5rem;
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	#left-bar #logo {
		color: #fff;
		font-size: 1rem;
		margin-block: 1.5rem;
	}
	#left-bar img {
		width: 1.8rem;
	}
	#left-bar .selected {
		background-color: #555;
		border-radius: 0.4rem;
	}
	#left-bar .space {
		margin-block: 0.5rem;
	}
	#content {
		flex: 1;
		overflow: hidden;
	}
</style>
