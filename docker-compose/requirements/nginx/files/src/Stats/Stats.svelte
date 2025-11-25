<script lang="ts">
	import '@fortawesome/fontawesome-free/css/all.css';
	import { onMount } from 'svelte';

	export let menu: any;

	const serverUrl = '';
	let stats: any = null;
	let isLoading = true;

	menu.dominantColor = '#0d0d0d';
	menu.selected = 5;

	onMount(() => {
		if (menu.user.id !== -1) {
			fetchStats();
		}
	});

	$: if (menu.user.id !== -1 && !stats) {
		fetchStats();
	}

	function fetchStats() {
		fetch(serverUrl + '/api/get_user_stats', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({ idUser: menu.user.id }),
		})
		.then(res => res.json())
		.then(data => {
			stats = data;
			isLoading = false;
		})
		.catch(err => {
			console.error(err);
			isLoading = false;
		});
	}

	function formatWatchTime(hours: number): string {
		if (hours < 24) return `${hours}h`;
		const days = Math.floor(hours / 24);
		const remainingHours = hours % 24;
		return remainingHours > 0 ? `${days}j ${remainingHours}h` : `${days}j`;
	}
</script>

<main>
	{#if isLoading}
		<div class="loading">
			<div class="loader"></div>
		</div>
	{:else if stats}
		<div class="profile">
			<!-- Hero Section -->
			<div class="hero">
				<div class="hero-bg"></div>
				<div class="hero-content">
					<div class="avatar">
						<span>{menu.user.name?.charAt(0).toUpperCase() || '?'}</span>
					</div>
					<div class="hero-text">
						<h1>{menu.user.name}</h1>
						<p>Membre depuis {stats.first_watch ? new Date(stats.first_watch).getFullYear() : 'récemment'}</p>
					</div>
				</div>
				<div class="hero-stats">
					<div class="hero-stat">
						<span class="big-number">{formatWatchTime(stats.total_watch_time_hours)}</span>
						<span class="label">de visionnage</span>
					</div>
				</div>
			</div>

			<!-- Bento Grid -->
			<div class="bento">
				<!-- Episodes Count - Large -->
				<div class="bento-item large episodes">
					<span class="bento-number">{stats.total_episodes}</span>
					<span class="bento-label">épisodes</span>
					<div class="bento-decoration">
						<i class="fas fa-play"></i>
					</div>
				</div>

				<!-- Anime Started -->
				<div class="bento-item anime-count">
					<span class="bento-number">{stats.total_anime}</span>
					<span class="bento-label">anime</span>
				</div>

				<!-- Completed -->
				<div class="bento-item completed">
					<span class="bento-number">{stats.anime_completed}</span>
					<span class="bento-label">terminés</span>
					<div class="completion-ring">
						<svg viewBox="0 0 36 36">
							<path
								d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
								fill="none"
								stroke="rgba(255,255,255,0.1)"
								stroke-width="3"
							/>
							<path
								d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
								fill="none"
								stroke="#f59e0b"
								stroke-width="3"
								stroke-dasharray="{stats.completion_rate}, 100"
								stroke-linecap="round"
							/>
						</svg>
						<span>{stats.completion_rate}%</span>
					</div>
				</div>

				<div class="bento-item language">
					<div class="lang-split">
						<div class="lang-side vostfr" style="flex: {stats.vostfr_count || 1}">
							<span class="lang-label">VOSTFR</span>
							<span class="lang-count">{stats.vostfr_count}</span>
						</div>
						<div class="lang-side vf" style="flex: {stats.vf_count || 1}">
							<span class="lang-label">VF</span>
							<span class="lang-count">{stats.vf_count}</span>
						</div>
					</div>
				</div>

				{#if stats.top_genres && stats.top_genres.length > 0}
					<div class="bento-item genre">
						<span class="genre-main">{stats.top_genres[0]?.name || '-'}</span>
						<span class="bento-label">genre favori</span>
						{#if stats.top_genres.length > 1}
							<div class="genre-others">
								{#each stats.top_genres.slice(1, 4) as g}
									<span class="genre-tag">{g.name}</span>
								{/each}
							</div>
						{/if}
					</div>
				{/if}

				<div class="bento-item wide activity">
					<span class="bento-label">activité</span>
					<div class="week-grid">
						{#each ['D', 'L', 'M', 'M', 'J', 'V', 'S'] as day, i}
							{@const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']}
							{@const dayData = stats.activity_by_day?.find((d) => d.day === dayNames[i])}
							{@const count = dayData?.count || 0}
							{@const maxCount = Math.max(...(stats.activity_by_day?.map((d) => d.count) || [1]))}
							{@const intensity = maxCount > 0 ? count / maxCount : 0}
							<div class="day-cell" style="--intensity: {intensity}" title="{dayNames[i]}: {count}">
								<span class="day-letter">{day}</span>
							</div>
						{/each}
					</div>
				</div>
			</div>

			{#if stats.top_anime && stats.top_anime.length > 0}
				<section class="top-section">
					<h2>Les plus regardés</h2>
					<div class="top-list">
						{#each stats.top_anime.slice(0, 5) as anime, i}
							<div class="top-item" style="--delay: {i * 0.1}s">
								<span class="rank" class:gold={i === 0} class:silver={i === 1} class:bronze={i === 2}>
									{i + 1}
								</span>
								<img src={anime.img} alt={anime.title} />
								<div class="top-info">
									<span class="top-title">{anime.title}</span>
									<span class="top-meta">{anime.episodes} ep.</span>
								</div>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			{#if stats.recent_activity && stats.recent_activity.length > 0}
				<section class="recent-section">
					<h2>Récemment</h2>
					<div class="recent-scroll">
						{#each stats.recent_activity as activity}
							<div class="recent-card">
								<img src={activity.img} alt={activity.title} />
								<div class="recent-overlay">
									<span class="recent-ep">EP {activity.episode}</span>
								</div>
							</div>
						{/each}
					</div>
				</section>
			{/if}
		</div>
	{:else}
		<div class="empty">
			<div class="empty-icon">
				<i class="fas fa-ghost"></i>
			</div>
			<p>Rien à voir ici...</p>
			<span>Regarde quelques anime d'abord !</span>
		</div>
	{/if}
</main>

<style>
	main {
		flex: 1;
		height: 100%;
		color: white;
		overflow-y: auto;
		overflow-x: hidden;
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
	}

	.loader {
		width: 40px;
		height: 40px;
		border: 3px solid rgba(255, 255, 255, 0.1);
		border-top-color: #f59e0b;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	.profile {
		max-width: 900px;
		margin: 0 auto;
		padding: 0 1.5rem 3rem;
	}

	/* Hero */
	.hero {
		position: relative;
		padding: 3rem 2rem;
		margin-bottom: 1.5rem;
		border-radius: 1.5rem;
		overflow: hidden;
	}

	.hero-bg {
		position: absolute;
		inset: 0;
		background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f1a 100%);
		opacity: 0.8;
	}

	.hero-bg::before {
		content: '';
		position: absolute;
		inset: 0;
		background: radial-gradient(circle at 70% 30%, rgba(245, 158, 11, 0.15), transparent 50%);
	}

	.hero-content {
		position: relative;
		display: flex;
		align-items: center;
		gap: 1.25rem;
		margin-bottom: 2rem;
	}

	.avatar {
		width: 70px;
		height: 70px;
		border-radius: 50%;
		background: linear-gradient(135deg, #f59e0b, #d97706);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.75rem;
		font-weight: 700;
		box-shadow: 0 8px 32px rgba(245, 158, 11, 0.3);
	}

	.hero-text h1 {
		font-size: 1.5rem;
		font-weight: 700;
		margin-bottom: 0.25rem;
	}

	.hero-text p {
		color: rgba(255, 255, 255, 0.5);
		font-size: 0.9rem;
	}

	.hero-stats {
		position: relative;
		display: flex;
		justify-content: center;
	}

	.hero-stat {
		text-align: center;
	}

	.big-number {
		display: block;
		font-size: 3.5rem;
		font-weight: 800;
		line-height: 1;
		background: linear-gradient(135deg, #fff, rgba(255,255,255,0.7));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.hero-stat .label {
		color: rgba(255, 255, 255, 0.5);
		font-size: 0.95rem;
	}

	.bento {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.bento-item {
		background: rgba(255, 255, 255, 0.03);
		border: 1px solid rgba(255, 255, 255, 0.06);
		border-radius: 1.25rem;
		padding: 1.25rem;
		position: relative;
		overflow: hidden;
		transition: transform 0.2s, border-color 0.2s;
	}

	.bento-item:hover {
		transform: translateY(-2px);
		border-color: rgba(255, 255, 255, 0.1);
	}

	.bento-item.large {
		grid-column: span 2;
		grid-row: span 2;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		text-align: center;
	}

	.bento-item.wide {
		grid-column: span 2;
	}

	.bento-number {
		font-size: 2.5rem;
		font-weight: 800;
		line-height: 1;
		display: block;
	}

	.bento-item.large .bento-number {
		font-size: 5rem;
	}

	.bento-label {
		color: rgba(255, 255, 255, 0.4);
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.bento-decoration {
		position: absolute;
		right: -20px;
		bottom: -20px;
		font-size: 8rem;
		color: rgba(255, 255, 255, 0.03);
	}

	.episodes {
		background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), transparent);
	}

	.episodes .bento-number {
		color: #f59e0b;
	}

	.completed {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.completion-ring {
		position: absolute;
		right: 1rem;
		top: 50%;
		transform: translateY(-50%);
		width: 50px;
		height: 50px;
	}

	.completion-ring svg {
		width: 100%;
		height: 100%;
		transform: rotate(-90deg);
	}

	.completion-ring span {
		position: absolute;
		inset: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.7rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.6);
	}

	.language {
		padding: 0;
		overflow: hidden;
	}

	.lang-split {
		display: flex;
		height: 100%;
		min-height: 100px;
	}

	.lang-side {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 1rem;
		transition: flex 0.3s ease;
	}

	.lang-side.vostfr {
		background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.05));
	}

	.lang-side.vf {
		background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.05));
	}

	.lang-label {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: rgba(255, 255, 255, 0.5);
		margin-bottom: 0.25rem;
	}

	.lang-count {
		font-size: 1.25rem;
		font-weight: 700;
	}

	.genre {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.genre-main {
		font-size: 1.4rem;
		font-weight: 700;
	}

	.genre-others {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-top: 0.5rem;
	}

	.genre-tag {
		font-size: 0.7rem;
		padding: 0.2rem 0.5rem;
		background: rgba(255, 255, 255, 0.08);
		border-radius: 1rem;
		color: rgba(255, 255, 255, 0.6);
	}

	.activity {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.week-grid {
		display: flex;
		gap: 0.5rem;
		justify-content: space-between;
	}

	.day-cell {
		flex: 1;
		aspect-ratio: 1;
		max-width: 60px;
		border-radius: 0.75rem;
		background: rgba(245, 158, 11, calc(var(--intensity) * 0.5 + 0.05));
		display: flex;
		align-items: center;
		justify-content: center;
		transition: transform 0.2s;
	}

	.day-cell:hover {
		transform: scale(1.1);
	}

	.day-letter {
		font-size: 0.75rem;
		font-weight: 600;
		color: rgba(255, 255, 255, calc(var(--intensity) * 0.5 + 0.4));
	}

	/* Top Section */
	.top-section {
		margin-bottom: 2rem;
	}

	.top-section h2, .recent-section h2 {
		font-size: 1rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.6);
		margin-bottom: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.top-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.top-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 0.75rem 1rem;
		background: rgba(255, 255, 255, 0.02);
		border-radius: 1rem;
		transition: background 0.2s;
		animation: slideIn 0.3s ease backwards;
		animation-delay: var(--delay);
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateX(-10px);
		}
	}

	.top-item:hover {
		background: rgba(255, 255, 255, 0.05);
	}

	.rank {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.1);
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		font-size: 0.85rem;
	}

	.rank.gold {
		background: linear-gradient(135deg, #f59e0b, #d97706);
		color: #000;
	}

	.rank.silver {
		background: linear-gradient(135deg, #9ca3af, #6b7280);
		color: #000;
	}

	.rank.bronze {
		background: linear-gradient(135deg, #d97706, #92400e);
		color: #000;
	}

	.top-item img {
		width: 45px;
		height: 62px;
		object-fit: cover;
		border-radius: 0.5rem;
	}

	.top-info {
		flex: 1;
		min-width: 0;
	}

	.top-title {
		display: block;
		font-weight: 500;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.top-meta {
		font-size: 0.8rem;
		color: rgba(255, 255, 255, 0.4);
	}

	.recent-section {
		margin-bottom: 2rem;
	}

	.recent-scroll {
		display: flex;
		gap: 0.75rem;
		overflow-x: auto;
		padding-bottom: 0.5rem;
		scrollbar-width: none;
	}

	.recent-scroll::-webkit-scrollbar {
		display: none;
	}

	.recent-card {
		position: relative;
		flex-shrink: 0;
		width: 100px;
		height: 140px;
		border-radius: 0.75rem;
		overflow: hidden;
	}

	.recent-card img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.recent-overlay {
		position: absolute;
		inset: 0;
		background: linear-gradient(to top, rgba(0,0,0,0.8), transparent 50%);
		display: flex;
		align-items: flex-end;
		justify-content: center;
		padding-bottom: 0.5rem;
	}

	.recent-ep {
		font-size: 0.7rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.9);
	}

	/* Empty */
	.empty {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
		color: rgba(255, 255, 255, 0.5);
	}

	.empty-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
		opacity: 0.3;
		animation: float 3s ease-in-out infinite;
	}

	@keyframes float {
		0%, 100% { transform: translateY(0); }
		50% { transform: translateY(-10px); }
	}

	.empty p {
		font-size: 1.1rem;
		color: rgba(255, 255, 255, 0.7);
		margin-bottom: 0.25rem;
	}

	.empty span {
		font-size: 0.9rem;
	}

	@media (max-width: 700px) {
		.bento {
			grid-template-columns: repeat(2, 1fr);
		}

		.bento-item.large {
			grid-column: span 2;
		}

		.bento-item.wide {
			grid-column: span 2;
		}

		.hero {
			padding: 2rem 1.5rem;
		}

		.big-number {
			font-size: 2.5rem;
		}

		.bento-item.large .bento-number {
			font-size: 3.5rem;
		}
	}
</style>
