<script lang='ts'>
	export let menu: any;

	console.log(menu);
</script>

<main>
	<div class='tile left-part'>
		<div id="player">
			<!-- svelte-ignore a11y_media_has_caption -->
			<video src="http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4" autoplay>
			</video>
		</div>
	</div>
	<div class='tile right-part'>

	</div>
</main>

<style>
	main {
		display: flex;
		height: 100%;
		width: 100%;
		padding: 1rem;
		position: relative;
		flex-direction: row;
		justify-content: space-between;
	}
	.tile {
		border-radius: 0.5rem;
		background-color: #c7c7c75c;
		border: 1px solid #c7c7c72b;
		box-shadow: 0 0 5px #0000003b
	}
	.left-part {
		width: 70%;
		height: 100%;
		margin-right: 1rem;

	}
	.right-part {
		width: 30%;
		min-width: 200px;
		height: 100%;
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

</style>