<script lang='ts'>
	import Loader from "../Global/Loader.svelte";

	export	let		menu: any;

	const	banGenre				= ['vostfr', 'vf', 'cardlistanime', 'anime', '-', 'scans', 'film'];
	const	serverUrl				= 'http://localhost:8080';
	const	base_url_tmdb			= 'https://image.tmdb.org/t/p/original';
	const	anime					= menu.data;
	let		imageLoaded				= false;
	let		backgroundImg			= '';
	let		logoImg					= '';
	let		genreString: string[]	= [];
	let		allSeasons				= [];
	let		dataFromTmdb			= {
										title: '',
										firstAirDate: '',
										name: '',
										originalName: '',
										overview: '',
										poster: '',
										popularity: 0,
										note: 0,
										nbVotes: 0,
										noData: false,
										fetch: false
									};

	anime?.genre?.map((genre: string) => {
		if (!banGenre.includes(genre.toLowerCase()))
			genreString?.push(genre); 
	});

	const get_data_from_tmdb = async (id: string, isMovie: boolean) => {
		let allDiff: any = [];
		let response = null;
		let data = null;
		let url = null;
		let allAnimeData = [];

		if (!isMovie)
		{
			url = `https://api.themoviedb.org/3/search/tv?{api_key_tmdb}&query=${id}&language=fr-FR`;
			response = await fetch(serverUrl + '/api/tmdb', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({url: url}),
			});
			data = await response.json();
			allAnimeData = data?.results.filter((result: any) => result.genre_ids.includes(16));
		}
		else
		{
			url = `https://api.themoviedb.org/3/search/movie?{api_key_tmdb}&query=${id}&language=fr-FR`;
			response = await fetch(serverUrl + '/api/tmdb', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({url: url}),
			});
			data = await response.json();
			allAnimeData = data?.results.filter((result: any) => result.genre_ids.includes(16));
		}
		if (allAnimeData.length === 0)
		{
			dataFromTmdb.noData = true;
			dataFromTmdb.title = ''
			dataFromTmdb.firstAirDate = ''
			dataFromTmdb.name = ''
			dataFromTmdb.originalName = ''
			dataFromTmdb.overview = ''
			dataFromTmdb.poster = ''
			dataFromTmdb.popularity = 0
			dataFromTmdb.note = 0
			dataFromTmdb.nbVotes = 0
			dataFromTmdb.fetch = true;
			return (null);
		}
		console.log(allAnimeData);
		for (let i = 0; i < allAnimeData.length; i++)
			allDiff.push(allAnimeData[i][isMovie ? 'title' : 'name'].length - id.length);
		
		let animeData = allAnimeData[allDiff.indexOf(Math.min(...allDiff))];
		let idAnime: number = animeData?.id;
		
		dataFromTmdb.title = animeData.title ? animeData.title : animeData.name;
		dataFromTmdb.firstAirDate = animeData.first_air_date ? animeData.first_air_date : animeData.release_date;
		dataFromTmdb.name = animeData.name;
		dataFromTmdb.originalName = animeData.original_name;
		dataFromTmdb.overview = animeData.overview;
		dataFromTmdb.poster = base_url_tmdb + animeData.poster_path
		dataFromTmdb.popularity = animeData.popularity;
		dataFromTmdb.note = animeData.vote_average;
		dataFromTmdb.nbVotes = animeData.vote_count;
		dataFromTmdb.noData = false;

		url = `https://api.themoviedb.org/3/${isMovie ? 'movie' : 'tv'}/${idAnime}/images?{api_key_tmdb}&include_image_language=ja,en,null`;
		response = await fetch(serverUrl + '/api/tmdb', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({url: url}),
		});
		data = await response.json();
		if (data.logos.length === 0) 
		{
			const fallbackUrl = `https://api.themoviedb.org/3/${isMovie ? 'movie' : 'tv'}/${idAnime}/images?{api_key_tmdb}`;
			response = await fetch(serverUrl + '/api/tmdb', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({url: fallbackUrl}),
			});
			data = await response.json();
		}
		dataFromTmdb.fetch = true;
		return (data);
	}

	fetch(serverUrl + '/api/get_anime_season', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({url: anime.url, serverUrl: serverUrl}),
	}).then((response) => {
		return response.json();
	}).then((data) => {
		let season = data.season;
		let isMovie = false;

		if (anime?.genre.includes('Vf'))
		{
			data.season.forEach((element: string) => {
				element = element.replace('vostfr', 'vf');
				season.push(element);
			});
		}
		allSeasons = season;
		isMovie = season[0]?.toLowerCase().includes('film');
		get_data_from_tmdb(anime.title, isMovie).then((data) => {
			if (!data)
			{
				imageLoaded = true;
				dataFromTmdb.fetch = true;
			}
			const	logoData = data?.logos[0];
			const	backdropData = data?.backdrops[0];

			if (logoData)
				logoImg = base_url_tmdb + logoData.file_path;
			if (backdropData)
				backgroundImg = base_url_tmdb + backdropData.file_path;
		});
	}).catch((error) => {
		console.warn(error);
	});

</script>

<main>
	<div class='bg-container'>
		<div class="linear-gradient"></div>
		<img
			src={anime.img}
			alt={menu.data.title}
			class='{imageLoaded && !dataFromTmdb.noData ? "hideBg" : "bg"}'
			style='z-index: 2;'
		/>
		<img
			src={backgroundImg}
			alt={menu.data.title}
			class='bg'
			on:load={() => {imageLoaded = true}}
		/>
	</div>
	{#if imageLoaded && dataFromTmdb.fetch}
		<div class="left">
			{#if logoImg}
				<img src={logoImg} alt={menu.data.title}/>
			{/if}
			<h1>{anime.title}</h1>
			<p class="genre" style="text-align: center;">{genreString.join(', ')}</p>
			{#if logoImg}
				<div class="line" style="border-top: 1px solid #fff;">
					<p class="type">Date de sortie</p>
					<p>{new Date(dataFromTmdb.firstAirDate).toLocaleDateString()}</p>
				</div>
				<div class="line">
					<p class="type">Popularité</p>
					<p>{dataFromTmdb.popularity}</p>
				</div>
				<div class="line" style="margin-bottom: 2rem;">
					<p class="type">Note</p>
					<p>{dataFromTmdb.note}/10 ({dataFromTmdb.nbVotes} votes)</p>
				</div>
				<p>{dataFromTmdb.overview}</p>
			{:else}
				<p>Aucune information disponible</p>
			{/if}
		</div>
		<div class='bg-button'>
			<button class="see-button" on:click={() => {
				menu.data = {
					anime: anime,
					tmdb: dataFromTmdb
				}
				menu.selected = 4;
			}}>Regarder</button>
		</div>
	{:else}
		<div class="center">
			<Loader scale={2} />
			<div class="center">
				<p style="margin-top: 8rem;">Chargement</p>
			</div>
		</div>
	{/if}
	
</main>

<style>
	main {
		flex: 1;
		height: 100%;
		position: relative;
	}
	.center {
		position: absolute;
		top: 50%;
		z-index: 999;
		left: 50%;
		transform: translate(-50%, -50%);
		color: #fff;
	}
	.bg-container {
		width: 100%;
		height: 100%;
		position: absolute;
		top: 0;
		left: 0;
	}
	.bg {
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		z-index: 0;
		object-fit: cover;
		border-top-right-radius: 0.5rem;
		border-bottom-right-radius: 0.5rem;
		object-position: center;
		position: absolute;
		top: 0;
		left: 0;
		animation: showBgAnime 0.5s;
	}
	.hideBg {
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		z-index: 0;
		object-fit: cover;
		border-top-right-radius: 0.5rem;
		border-bottom-right-radius: 0.5rem;
		object-position: center;
		position: absolute;
		top: 0;
		left: 0;
		animation: fadeOut 0.5s;
		opacity: 0;
	}
	.linear-gradient {
		width: 100%;
		height: 100%;
		position: absolute;
		top: 0;
		left: 0;
		z-index: 3;
		background: linear-gradient(90deg,
			rgba(51, 51, 51, 1) 0%,
			rgba(51, 51, 51, 1) 1%,
			rgba(51, 51, 51, 0.4) 50%,
			rgba(0,0,0,0) 100%
		);
	}
	.left {
		width: 50%;
		max-width: 30rem;
		height: 100%;
		position: absolute;
		top: 0;
		left: 0;
		z-index: 4;
		display: flex;
		flex-direction: column;
		align-items: center;
		color: #fff;
		padding: 2vw;
		overflow-y: scroll;
	}
	.left::-webkit-scrollbar {
		width: 0;
	}
	.left img {
		width: 100%;
		height: 10rem;
		object-fit: contain;
	}
	.left h1 {
		font-size: 1.5rem;
		margin: 1rem 0;
		text-align: center;
	}
	.left p {
		font-size: 1rem;
		text-align: justify;
	}
	.genre {
		font-size: 1rem;
		margin-bottom: 1rem;
	}
	.line {
		display: flex;
		justify-content: space-between;
		width: 90%;
		padding: 0.5rem;
		border-bottom: 1px solid #fff;
	}
	.line .type {
		font-weight: bold;
	}
	.see-button {
		background-color: #333;
		color: #fff;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		cursor: pointer;
	}

	.bg-button {
		position: absolute;
		bottom: 2rem;
		right: 2rem;
		z-index: 4;
		padding: 2px;
		border-radius: 0.5rem;
		background: linear-gradient(90deg, #333, #666, #999, #ccc, #999, #666, #333);
		animation: rotate-colors 3s linear infinite;
		background-size: 300%;
	}

	@keyframes rotate-colors {
		0% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 200% 50%;
		}
		100% {
			background-position: 0% 50%;
		}
	}
</style>