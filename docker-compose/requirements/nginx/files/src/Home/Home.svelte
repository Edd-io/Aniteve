<script lang="ts">
	import '@fortawesome/fontawesome-free/css/all.css';
	import { onMount } from 'svelte';
	import { navigate } from 'svelte-routing';
	import AnimeCard from './AnimeCard.svelte';

	export let menu: any;

	const serverUrl = '';
	let homeData: any = { sections: [] };
	let genreAnime: any[] = [];
	let progressData: any = [];
	let isLoading = true;
	let buttonActive = false;
	let lastGenre: string | null = null;

	menu.dominantColor = '#0d0d0d';
	menu.selected = 0;

	$: resumeAnime = progressData?.filter ? progressData.filter((item: any) => item.completed === 0 || item.completed === 2) : [];

	let progressFetched = false;

	onMount(() => {
		if (menu.selectedGenre) {
			fetchGenreAnime(menu.selectedGenre);
		} else {
			fetchHomeData();
		}
	});

	$: if (menu.selectedGenre !== lastGenre) {
		lastGenre = menu.selectedGenre;
		if (menu.selectedGenre) {
			fetchGenreAnime(menu.selectedGenre);
		} else if (lastGenre !== null) {
			fetchHomeData();
		}
	}

	$: if (menu.user.id !== -1 && !progressFetched) {
		progressFetched = true;
		getDataProgress();
	}

	function fetchHomeData() {
		isLoading = true;
		genreAnime = [];
		fetch(serverUrl + '/api/get_home_data', {
			method: 'GET',
			headers: {
				'Authorization': localStorage.getItem('token') || ''
			}
		})
		.then(res => res.json())
		.then(data => {
			homeData = data;
			isLoading = false;
		})
		.catch(err => {
			console.error(err);
			isLoading = false;
		});
	}

	function fetchGenreAnime(genre: string) {
		isLoading = true;
		fetch(serverUrl + '/api/get_anime_by_genre?genre=' + encodeURIComponent(genre) + '&limit=50', {
			method: 'GET',
			headers: {
				'Authorization': localStorage.getItem('token') || ''
			}
		})
		.then(res => res.json())
		.then(data => {
			genreAnime = data;
			isLoading = false;
		})
		.catch(err => {
			console.error(err);
			isLoading = false;
		});
	}

	function clearGenreFilter() {
		menu.selectedGenre = null;
	}

	function getDataProgress() {
		if (menu.user.id === -1) return;

		fetch(serverUrl + '/api/get_all_progress', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({idUser: menu.user.id}),
		})
		.then(response => response.json())
		.then(json => {
			progressData = json || [];
		})
		.catch(error => {
			console.warn(error);
		});
	}

	function selectAnime(anime: any, elementId: string) {
		if (buttonActive) return;
		buttonActive = true;

		const element = document.getElementById(elementId);
		if (element) {
			element.style.animation = 'choose 0.4s ease-out';
			element.style.opacity = '0';
		}

		setTimeout(() => {
			menu.data = anime;
			menu.selected = 4;
			navigate('/player', {replace: true});
		}, 350);
	}

	function scrollSection(sectionId: string, direction: number) {
		const section = document.getElementById(sectionId);
		if (section) {
			section.scrollBy({ left: direction * 300, behavior: 'smooth' });
		}
	}
</script>

<main>
	{#if isLoading}
		<div class="loading">
			<i class="fas fa-spinner fa-spin"></i>
		</div>
	{:else if menu.selectedGenre}
		<!-- Genre Filter Results -->
		<section class="section">
			<div class="section-header">
				<div class="genre-header">
					<h2>{menu.selectedGenre}</h2>
					<button class="clear-filter-btn" on:click={clearGenreFilter}>
						<i class="fas fa-times"></i>
						Effacer le filtre
					</button>
				</div>
			</div>
			{#if genreAnime.length > 0}
				<div class="cards-grid full-grid">
					{#each genreAnime as anime}
						<div id="genre-anime-{anime.id}">
							<AnimeCard
								{anime}
								onClick={() => selectAnime(anime, `genre-anime-${anime.id}`)}
							/>
						</div>
					{/each}
				</div>
			{:else}
				<div class="empty-state">
					<i class="fas fa-film"></i>
					<p>Aucun anime trouvé pour ce genre</p>
				</div>
			{/if}
		</section>
	{:else}
		<!-- Resume Section -->
		{#if resumeAnime.length > 0}
			<section class="section">
				<div class="section-header">
					<h2>Reprendre</h2>
					<div class="section-controls">
						<button class="scroll-btn" on:click={() => scrollSection('resume-scroll', -1)}>
							<i class="fas fa-chevron-left"></i>
						</button>
						<button class="scroll-btn" on:click={() => scrollSection('resume-scroll', 1)}>
							<i class="fas fa-chevron-right"></i>
						</button>
					</div>
				</div>
				<div class="cards-scroll" id="resume-scroll">
					{#each resumeAnime as item, i}
						<button
							class="resume-card"
							id="resume-{item.anime.id}"
							on:click={() => selectAnime(item.anime, `resume-${item.anime.id}`)}
						>
							<div class="resume-image">
								<img src={item.poster} alt={item.anime.title} />
								<div class="progress-bar-container">
									<div class="progress-bar" style="width: {item.progress}%"></div>
								</div>
								{#if item.completed === 2}
									<span class="new-badge">Nouveau</span>
								{/if}
							</div>
							<div class="resume-info">
								<h4>{item.anime.title.length > 20 ? item.anime.title.slice(0, 20) + '...' : item.anime.title}</h4>
								<p>Ep. {item.episode} {item.season_name ? '• ' + item.season_name : ''}</p>
							</div>
						</button>
					{/each}
				</div>
			</section>
		{/if}

		{#each homeData.sections as section, sectionIndex}
			{#if section.anime && section.anime.length > 0}
				<section class="section">
					<div class="section-header">
						<h2>{section.title}</h2>
						<div class="section-controls">
							<button class="scroll-btn" on:click={() => scrollSection(`section-${sectionIndex}`, -1)}>
								<i class="fas fa-chevron-left"></i>
							</button>
							<button class="scroll-btn" on:click={() => scrollSection(`section-${sectionIndex}`, 1)}>
								<i class="fas fa-chevron-right"></i>
							</button>
						</div>
					</div>
					<div class="cards-grid" id="section-{sectionIndex}">
						{#each section.anime as anime}
							<div id="anime-{sectionIndex}-{anime.id}">
								<AnimeCard
									{anime}
									onClick={() => selectAnime(anime, `anime-${sectionIndex}-${anime.id}`)}
								/>
							</div>
						{/each}
					</div>
				</section>
			{/if}
		{/each}
	{/if}
</main>

<style>
	main {
		flex: 1;
		height: 100%;
		color: white;
		padding: 1.5rem 2rem;
		overflow-y: auto;
		overflow-x: hidden;
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		font-size: 2rem;
		color: rgba(255, 255, 255, 0.5);
	}

	.section {
		margin-bottom: 2.5rem;
	}

	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1.25rem;
	}

	.section-header h2 {
		font-size: 1.4rem;
		font-weight: 600;
		color: #ffffff;
	}

	.genre-header {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.clear-filter-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background-color: rgba(255, 255, 255, 0.1);
		border: none;
		border-radius: 0.5rem;
		color: rgba(255, 255, 255, 0.7);
		font-size: 0.85rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.clear-filter-btn:hover {
		background-color: rgba(255, 255, 255, 0.2);
		color: #ffffff;
	}

	.clear-filter-btn i {
		font-size: 0.75rem;
	}

	.section-controls {
		display: flex;
		gap: 0.5rem;
	}

	.scroll-btn {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background-color: rgba(255, 255, 255, 0.1);
		border: none;
		color: rgba(255, 255, 255, 0.7);
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s;
	}

	.scroll-btn:hover {
		background-color: rgba(255, 255, 255, 0.2);
		color: #ffffff;
	}

	.scroll-btn i {
		font-size: 0.8rem;
	}

	.cards-scroll {
		display: flex;
		gap: 1rem;
		overflow-x: auto;
		padding-bottom: 0.5rem;
		scroll-behavior: smooth;
	}

	.cards-scroll::-webkit-scrollbar {
		display: none;
	}

	.cards-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1rem;
	}

	@media (max-width: 1400px) {
		.cards-grid {
			grid-template-columns: repeat(3, 1fr);
		}
	}

	@media (max-width: 1000px) {
		.cards-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	.full-grid {
		grid-template-columns: repeat(5, 1fr);
	}

	@media (max-width: 1400px) {
		.full-grid {
			grid-template-columns: repeat(4, 1fr);
		}
	}

	@media (max-width: 1000px) {
		.full-grid {
			grid-template-columns: repeat(3, 1fr);
		}
	}

	@media (max-width: 700px) {
		.full-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		color: rgba(255, 255, 255, 0.5);
		gap: 1rem;
	}

	.empty-state i {
		font-size: 3rem;
		opacity: 0.3;
	}

	.empty-state p {
		font-size: 1rem;
	}

	.resume-card {
		display: flex;
		flex-direction: column;
		background: none;
		border: none;
		cursor: pointer;
		text-align: left;
		color: #ffffff;
		min-width: 140px;
		transition: transform 0.2s;
	}

	.resume-card:hover {
		transform: scale(1.03);
	}

	.resume-image {
		position: relative;
		width: 140px;
		height: 200px;
		border-radius: 0.5rem;
		overflow: hidden;
	}

	.resume-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.progress-bar-container {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 4px;
		background-color: rgba(0, 0, 0, 0.5);
	}

	.progress-bar {
		height: 100%;
		background-color: #f59e0b;
		transition: width 0.3s;
	}

	.new-badge {
		position: absolute;
		top: 0.5rem;
		left: 0.5rem;
		background-color: #f59e0b;
		color: #000000;
		font-size: 0.65rem;
		font-weight: 600;
		padding: 0.2rem 0.5rem;
		border-radius: 0.25rem;
	}

	.resume-info {
		margin-top: 0.5rem;
	}

	.resume-info h4 {
		font-size: 0.85rem;
		font-weight: 500;
		margin-bottom: 0.2rem;
	}

	.resume-info p {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.5);
	}
</style>
