<script lang="ts">
	import '@fortawesome/fontawesome-free/css/all.css';

	export let anime: any;
	export let onClick: () => void;

	function getRandomRating(): string {
		return (7 + Math.random() * 2.5).toFixed(1);
	}

	function getTypeLabel(): string {
		if (anime.genre && anime.genre.length > 0) {
			return anime.genre[0];
		}
		return 'Anime';
	}
</script>

<button class="anime-card" on:click={onClick}>
	<div class="card-image">
		<img src={anime.img} alt={anime.title} />
		<div class="card-gradient"></div>
		<div class="card-content">
			<h3 class="title">{anime.title.length > 30 ? anime.title.slice(0, 30) + '...' : anime.title}</h3>
			<div class="meta">
				<span class="rating">
					<i class="fas fa-star"></i> {getRandomRating()}
				</span>
				<span class="separator">|</span>
				<span class="type">{getTypeLabel()}</span>
			</div>
		</div>
	</div>
</button>

<style>
	.anime-card {
		position: relative;
		cursor: pointer;
		background: none;
		border: none;
		padding: 0;
		text-align: left;
		border-radius: 0.75rem;
		overflow: hidden;
		transition: transform 0.3s ease, box-shadow 0.3s ease;
	}

	.anime-card:hover {
		transform: scale(1.03);
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
	}

	.anime-card:hover .card-image img {
		transform: scale(1.1);
	}

	.card-image {
		position: relative;
		width: 100%;
		aspect-ratio: 16 / 10;
		overflow: hidden;
	}

	.card-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		transition: transform 0.4s ease;
	}

	.card-gradient {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 70%;
		background: linear-gradient(transparent, rgba(0, 0, 0, 0.85));
		pointer-events: none;
	}

	.card-content {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		padding: 1rem;
		color: #ffffff;
	}

	.title {
		font-size: 0.95rem;
		font-weight: 600;
		margin-bottom: 0.4rem;
		line-height: 1.3;
		text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
	}

	.meta {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.8rem;
	}

	.rating {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		color: #f59e0b;
		font-weight: 500;
	}

	.rating i {
		font-size: 0.7rem;
	}

	.separator {
		color: rgba(255, 255, 255, 0.3);
	}

	.type {
		color: rgba(255, 255, 255, 0.7);
	}
</style>
