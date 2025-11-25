<script lang='ts'>
	import { navigate } from 'svelte-routing';
	import '@fortawesome/fontawesome-free/css/all.css';
	export let menu: any;

	const serverUrl = '';
	let password = '';
	let error = '';
	let isLoading = false;

	function connect() {
		if (!password) {
			error = 'Veuillez entrer un mot de passe';
			return;
		}

		isLoading = true;
		error = '';

		fetch(serverUrl + '/api/login', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({ password })
		})
		.then(res => res.json())
		.then(data => {
			isLoading = false;
			if (data.token) {
				localStorage.setItem('token', data.token);
				menu.selected = 8;
				navigate('/choose_user', {replace: true});
			} else {
				error = 'Mot de passe incorrect';
			}
		})
		.catch(() => {
			isLoading = false;
			error = 'Erreur de connexion au serveur';
		});
	}
</script>

<main>
	<div class="login-container">
		<div class="login-card">
			<div class="logo">
				<img src="/img/logo_black.png" alt="Aniteve" />
			</div>
			<h1>Aniteve</h1>
			<p class="subtitle">Connectez-vous pour continuer</p>

			{#if error}
				<div class="error-message">
					<i class="fas fa-exclamation-circle"></i>
					{error}
				</div>
			{/if}

			<form on:submit|preventDefault={connect}>
				<div class="input-group">
					<i class="fas fa-lock"></i>
					<input
						type="password"
						placeholder="Mot de passe"
						bind:value={password}
						disabled={isLoading}
					/>
				</div>
				<button type="submit" class="submit-btn" disabled={isLoading}>
					{#if isLoading}
						<i class="fas fa-spinner fa-spin"></i>
					{:else}
						Se connecter
					{/if}
				</button>
			</form>
		</div>
	</div>
</main>

<style>
	main {
		width: 100%;
		height: 100%;
		background-color: #0d0d0d;
	}

	.login-container {
		display: flex;
		justify-content: center;
		align-items: center;
		width: 100%;
		height: 100%;
	}

	.login-card {
		background-color: #1a1a1a;
		padding: 3rem;
		border-radius: 1rem;
		width: 100%;
		max-width: 380px;
		text-align: center;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
	}

	.logo {
		margin-bottom: 1.5rem;
	}

	.logo img {
		width: 60px;
		filter: invert(1);
		opacity: 0.9;
	}

	h1 {
		color: #ffffff;
		font-size: 1.8rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
	}

	.subtitle {
		color: rgba(255, 255, 255, 0.5);
		font-size: 0.9rem;
		margin-bottom: 2rem;
	}

	.error-message {
		background-color: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.3);
		color: #ef4444;
		padding: 0.75rem 1rem;
		border-radius: 0.5rem;
		margin-bottom: 1.5rem;
		font-size: 0.85rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		justify-content: center;
	}

	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.input-group {
		display: flex;
		align-items: center;
		background-color: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
		padding: 0 1rem;
		transition: background-color 0.2s;
	}

	.input-group:focus-within {
		background-color: rgba(255, 255, 255, 0.1);
	}

	.input-group i {
		color: rgba(255, 255, 255, 0.4);
		font-size: 0.9rem;
	}

	.input-group input {
		flex: 1;
		background: none;
		border: none;
		padding: 1rem 0.75rem;
		color: #ffffff;
		font-size: 0.95rem;
		outline: none;
	}

	.input-group input::placeholder {
		color: rgba(255, 255, 255, 0.4);
	}

	.input-group input:disabled {
		opacity: 0.5;
	}

	.submit-btn {
		background-color: #f59e0b;
		border: none;
		padding: 1rem;
		border-radius: 0.5rem;
		color: #000000;
		font-size: 0.95rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		margin-top: 0.5rem;
	}

	.submit-btn:hover:not(:disabled) {
		background-color: #fbbf24;
		transform: translateY(-1px);
	}

	.submit-btn:active:not(:disabled) {
		transform: translateY(0);
	}

	.submit-btn:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}
</style>
