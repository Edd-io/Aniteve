<script lang='ts'>
	import { navigate } from 'svelte-routing';
	import '@fortawesome/fontawesome-free/css/all.css';
	export let menu: any;

	let listUser: any[] = [];
	let showNewUser = false;
	let newUserName = '';
	const serverUrl = '';
	menu.selected = 8;

	function getUsers() {
		fetch(serverUrl + '/api/get_users', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
		})
		.then(response => response.json())
		.then(data => {
			listUser = data;
		})
		.catch((error) => {
			console.warn('Error:', error);
		});
	}

	function createUser() {
		if (!newUserName.trim()) return;

		fetch(serverUrl + '/api/add_user', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({ name: newUserName }),
		})
		.then(response => response.json())
		.then(data => {
			getUsers();
			showNewUser = false;
			newUserName = '';
		})
		.catch((error) => {
			console.warn('Error:', error);
		});
	}

	function selectUser(user: any) {
		localStorage.setItem('idUser', user.id);
		menu.user.id = user.id;
		menu.user.name = user.name;
		menu.selected = 0;
		navigate('/home', {replace: true});
	}

	function getInitials(name: string): string {
		return name.charAt(0).toUpperCase();
	}

	getUsers();
</script>

<main>
	<div class="choose-container">
		<h1>Qui regarde ?</h1>
		<div class="list-user">
			{#each listUser as user}
				<button class="btn-user" on:click={() => selectUser(user)}>
					<div class="avatar">
						<span>{getInitials(user.name)}</span>
					</div>
					<p class="user-name">{user.name}</p>
				</button>
			{/each}
			<button class="btn-new-user" on:click={() => showNewUser = true}>
				<div class="avatar add-avatar">
					<i class="fas fa-plus"></i>
				</div>
				<p class="user-name">Ajouter</p>
			</button>
		</div>
	</div>

	{#if showNewUser}
		<div class="modal-overlay" on:click={() => showNewUser = false}>
			<div class="modal" on:click|stopPropagation>
				<h2>Nouveau profil</h2>
				<form on:submit|preventDefault={createUser}>
					<div class="input-group">
						<i class="fas fa-user"></i>
						<input
							type="text"
							placeholder="Nom du profil"
							bind:value={newUserName}
							autofocus
						/>
					</div>
					<div class="modal-actions">
						<button type="button" class="btn-cancel" on:click={() => { showNewUser = false; newUserName = ''; }}>
							Annuler
						</button>
						<button type="submit" class="btn-create">
							Créer
						</button>
					</div>
				</form>
			</div>
		</div>
	{/if}
</main>

<style>
	main {
		display: flex;
		height: 100vh;
		width: 100vw;
		color: white;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		background-color: #0d0d0d;
	}

	.choose-container {
		text-align: center;
	}

	h1 {
		font-size: 2rem;
		font-weight: 600;
		margin-bottom: 3rem;
		color: #ffffff;
	}

	.list-user {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 2rem;
		max-width: 800px;
	}

	.btn-user, .btn-new-user {
		display: flex;
		flex-direction: column;
		align-items: center;
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
		transition: transform 0.2s;
	}

	.btn-user:hover, .btn-new-user:hover {
		transform: scale(1.05);
	}

	.avatar {
		width: 100px;
		height: 100px;
		border-radius: 0.75rem;
		background: linear-gradient(135deg, #f59e0b, #d97706);
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 0.75rem;
		transition: box-shadow 0.2s;
	}

	.btn-user:hover .avatar {
		box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.3);
	}

	.avatar span {
		font-size: 2.5rem;
		font-weight: 600;
		color: #000000;
	}

	.add-avatar {
		background: rgba(255, 255, 255, 0.1);
		border: 2px dashed rgba(255, 255, 255, 0.3);
	}

	.add-avatar i {
		font-size: 2rem;
		color: rgba(255, 255, 255, 0.5);
	}

	.btn-new-user:hover .add-avatar {
		background: rgba(255, 255, 255, 0.15);
		box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
	}

	.user-name {
		font-size: 0.95rem;
		color: rgba(255, 255, 255, 0.8);
		margin: 0;
		max-width: 100px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		background-color: rgba(0, 0, 0, 0.8);
		display: flex;
		justify-content: center;
		align-items: center;
		animation: fadeIn 0.2s;
	}

	.modal {
		background-color: #1a1a1a;
		padding: 2rem;
		border-radius: 1rem;
		width: 100%;
		max-width: 350px;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
	}

	.modal h2 {
		font-size: 1.3rem;
		font-weight: 600;
		margin-bottom: 1.5rem;
		text-align: center;
	}

	.input-group {
		display: flex;
		align-items: center;
		background-color: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
		padding: 0 1rem;
		margin-bottom: 1.5rem;
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

	.modal-actions {
		display: flex;
		gap: 0.75rem;
	}

	.btn-cancel, .btn-create {
		flex: 1;
		padding: 0.875rem;
		border-radius: 0.5rem;
		font-size: 0.9rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-cancel {
		background-color: rgba(255, 255, 255, 0.1);
		border: none;
		color: #ffffff;
	}

	.btn-cancel:hover {
		background-color: rgba(255, 255, 255, 0.15);
	}

	.btn-create {
		background-color: #f59e0b;
		border: none;
		color: #000000;
	}

	.btn-create:hover {
		background-color: #fbbf24;
	}
</style>
