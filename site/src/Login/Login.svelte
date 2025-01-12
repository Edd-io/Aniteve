<script lang='ts'>
	import { navigate } from 'svelte-routing';
	export let menu: any;

	const serverUrl = 'http://localhost:8080';

	function connect()
	{
		const password = document.querySelector('.input-password')?.value;
				
		fetch(serverUrl + '/api/login', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({ password })
		})
		.then(res => res.json())
		.then(data => {
			if (data.token)
			{
				localStorage.setItem('token', data.token);
				menu.selected = 8;
				navigate('/choose_user', {replace: true});
			}
			else
			{
				const invalidPasswordElement = document.querySelector('#invalid-password');
				if (invalidPasswordElement) {
					invalidPasswordElement.style.display = 'block';
				}
			}
		})
		.catch(() => {
			const invalidPasswordElement = document.querySelector('#invalid-password');
			if (invalidPasswordElement) {
				invalidPasswordElement.style.display = 'block';
			}
		});
	}
</script>

<main>
	<div style="display: flex; justify-content: center; align-items: center; width: 100vw; height: 100vh; flex-direction: column;">
		<div style="background-color: #c7c7c75c; padding: 20px; border-radius: 10px; display: flex; flex-direction: column; align-items: center;">
			<h1 style="color: white; margin: 1rem">Aniteve</h1>
			<p style="color: red; margin-bottom: 1rem; display: none;" id="invalid-password">Mot de passe incorrect</p>
			<form style="display: flex; flex-direction: column; margin-bottom: 1rem" on:submit|preventDefault={connect}>
				<input type="password" name="password" placeholder="Mot de passe" style="margin-bottom: 1rem" class="input-password" />
				<button type="submit" class="input-button">Se connecter</button>
			</form>
		</div>
	</div>
</main>

<style>
	.input-password {
		background-color: #c7c7c75c;
		border: none;
		padding: 10px;
		border-radius: 5px;
		color: white;
		margin-bottom: 1rem;
		width: 100%;
	}
	.input-password::placeholder {
		color: rgb(200, 200, 200);
	}
	.input-password:focus {
		background-color: white;
		color: #000;
		outline: none;
	}
	.input-button {
		background-color: #1D6196;
		border: none;
		padding: 10px;
		border-radius: 5px;
		color: white;
		width: 100%;
		cursor: pointer;
	}
	.input-button:hover {
		background-color: #1D6196af;
	}
	.input-button:active {
		background-color: #1D6196d0;
	}
</style>