<script lang='ts'>
	import { Link } from 'svelte-routing';
	import '@fortawesome/fontawesome-free/css/all.css';

	export let menu: any;
</script>

<nav id="left-bar">
	<div class="logo-container">
		<img src="/img/logo_black.png" alt="logo" id="logo" />
	</div>

	<div class="nav-icons">
		<Link to="/home" class="nav-icon {menu.selected === 0 ? 'active' : ''}" title="Accueil">
			<i class="fas fa-home"></i>
		</Link>
		<Link to="/list" class="nav-icon {menu.selected === 2 ? 'active' : ''}" title="Ma liste">
			<i class="fas fa-bookmark"></i>
		</Link>
		<Link to="/download" class="nav-icon {menu.selected === 6 ? 'active' : ''}" title="Téléchargements">
			<i class="fas fa-download"></i>
		</Link>
		<Link to="/stats" class="nav-icon {menu.selected === 5 ? 'active' : ''}" title="Statistiques">
			<i class="fas fa-chart-bar"></i>
		</Link>
		<Link to="/together" class="nav-icon {menu.selected === 7 ? 'active' : ''}" title="Ensemble">
			<i class="fas fa-users"></i>
		</Link>
	</div>

	<div class="nav-bottom">
		<Link to="/choose_user" class="nav-icon" title="Profil">
			<i class="fas fa-user"></i>
		</Link>
	</div>
</nav>

<style>
	#left-bar {
		width: 70px;
		height: 100%;
		background-color: #0d0d0d;
		border-right: 1px solid rgba(255, 255, 255, 0.05);
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 1rem 0;
	}

	.logo-container {
		margin-bottom: 2rem;
	}

	#logo {
		width: 2.5rem;
		filter: invert(1);
		opacity: 0.9;
	}

	.nav-icons {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	:global(.nav-icon) {
		width: 44px;
		height: 44px;
		border-radius: 0.75rem;
		display: flex;
		align-items: center;
		justify-content: center;
		color: rgba(255, 255, 255, 0.5);
		transition: all 0.2s ease;
		text-decoration: none;
		position: relative;
	}

	:global(.nav-icon:hover) {
		color: rgba(255, 255, 255, 0.9);
		background-color: rgba(255, 255, 255, 0.08);
	}

	:global(.nav-icon.active) {
		color: #f59e0b;
		background-color: rgba(245, 158, 11, 0.1);
	}

	:global(.nav-icon i) {
		font-size: 1.2rem;
	}

	.nav-bottom {
		margin-top: auto;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}
</style>
