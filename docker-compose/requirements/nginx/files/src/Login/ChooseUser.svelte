<script lang='ts'>
	import { navigate } from 'svelte-routing';
	export let menu: any;

	let listUser: any[] = []
	let showNewUser = false;
	const serverUrl = '';
	menu.selected = 8;

	function getUsers()
	{
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

	function createUser()
	{
		const name = document.querySelector('input').value;
		fetch(serverUrl + '/api/add_user', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localStorage.getItem('token') || '',
			},
			body: JSON.stringify({ name }),
		})
		.then(response => response.json())
		.then(data => {
			getUsers();
			showNewUser = false;
		})
		.catch((error) => {
			console.warn('Error:', error);
		});
	}
	getUsers();
</script>

<main>
	<h1>Qui êtes-vous ?</h1>
	<div class="list-user">
		{#each listUser as user}
			<button class="btn-user" on:click={() => {
				localStorage.setItem('idUser', user.id);
				menu.user.id = user.id;
				menu.user.name = user.name;
				menu.selected = 0;
				navigate('/home', {replace: true});
			}}>
				<p>{user.name}</p>
			</button>
		{/each}
		<button class="btn-new-user" on:click={() => showNewUser = true}>
			<p>Nouvel utilisateur</p>
		</button>
	</div>
	{#if showNewUser}
		<div class="new-user-bg">
			<div class='div-new-user'>
				<input type="text" placeholder="Nom de l'utilisateur">
				<button on:click={createUser}>Créer</button>
				<button on:click={() => showNewUser = false}>Annuler</button>
			</div>
		</div>
	{/if}
</main>

<style>
	main {
		display: flex;
		height: 100vh;
		width: 100vw;
		padding: 1rem;
		color: white;
		flex-direction: column;
		justify-content: center;
		align-items: center;
	}
	.btn-user {
		background-color: #c7c7c75c;
		color: white;
		border: none;
		padding: 1rem;
		margin: 1rem;
		cursor: pointer;
		border: 1px solid white;
		border-radius: 100%;
		width: 7rem;
		height: 7rem;
		transition: transform 0.2s, background-color 0.2s;
	}
	.btn-user:hover {
		background-color: #c7c7c7aa;
		transform: scale(1.1);
	}
	.list-user {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		margin-top: 2rem;
		max-height: 100%;
	}
	.btn-user p {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.btn-new-user {
		background-color: #00000000;
		color: white;
		border: none;
		padding: 1rem;
		margin: 1rem;
		cursor: pointer;
		border: 1px dashed white;
		border-radius: 100%;
		width: 7rem;
		height: 7rem;
		transition: transform 0.2s, background-color 0.2s;
	}
	.btn-new-user:hover {
		background-color: #c7c7c7aa;
		transform: scale(1.1);
	}
	.new-user-bg {
		position: absolute;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		background-color: #000000aa;
		display: flex;
		justify-content: center;
		align-items: center;
		flex-direction: column;
		transition: background-color 0.2s;
		animation: fadeIn 0.2s;
	}
	.div-new-user {
		background-color: #c7c7c7a7;
		padding: 1rem;
		border-radius: 0.5rem;
		display: flex;
		flex-direction: column;
		width: 20rem;
	}
	.div-new-user * {
		margin: 0.5rem;
	}
	.div-new-user input {
		padding: 0.5rem;
		border-radius: 0.5rem;
		border: none;
	}
	.div-new-user input:focus {
		outline: none;
	}
	.div-new-user button {
		background-color: #00000000;
		color: white;
		border: 1px solid white;
		padding: 0.5rem;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: background-color 0.2s;
	}
	.div-new-user button:hover {
		background-color: #c7c7c7aa;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
</style>