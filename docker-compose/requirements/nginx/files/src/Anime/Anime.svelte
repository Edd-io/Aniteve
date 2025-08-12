<script lang="ts">
	import { navigate } from "svelte-routing";
	import Loader from "../Global/Loader.svelte";

	export let menu: any;

	const banGenre = [
		"vostfr",
		"vf",
		"cardlistanime",
		"anime",
		"-",
		"scans",
		"film",
	];
	const serverUrl = "";
	const base_url_tmdb = "https://image.tmdb.org/t/p/original";
	const anime = menu.data;
	let progressData: any = [];
	let imageLoaded = false;
	let backgroundImg = "";
	let logoImg = "";
	let genreString: string[] = [];
	let allSeasons: Season[] = [];
	let dominantColor = "";
	let dataFromTmdb = {
		title: "",
		firstAirDate: "",
		name: "",
		originalName: "",
		overview: "",
		poster: "",
		popularity: 0,
		note: 0,
		nbVotes: 0,
		noData: false,
		fetch: false,
	};
	let animation = true;

	interface Season {
		name: string;
		url: string;
		lang: string;
	}

	console.log(anime);
	anime?.genre?.map((genre: string) => {
		if (!banGenre.includes(genre.toLowerCase())) genreString?.push(genre);
	});

	const createHeaders = (token: string | null) => ({
		"Content-Type": "application/json",
		Authorization: token || "",
	});

	interface TMDBSearchResult {
		id: number;
		title?: string;
		name?: string;
		original_name?: string;
		overview?: string;
		poster_path?: string;
		vote_average?: number;
		vote_count?: number;
		first_air_date?: string;
		release_date?: string;
		genre_ids?: number[];
		popularity?: number;
	}

	interface TMDBData {
		title?: string;
		overview?: string;
		poster_path?: string;
		vote_average?: number;
		first_air_date?: string;
		logos?: any[];
		backdrops?: backdropImage[];
		popularity?: number;
		vote_count?: number;
		posters?: any[];
		original_name?: string | null;
	}

	interface backdropImage {
		aspect_ratio: number;
		height: number;
		iso_639_1: string | null;
		file_path: string;
		vote_average: number;
		vote_count: number;
		width: number;
	}

	const get_data_from_tmdb = async (id: string, isMovie: boolean) => {
		async function callTMDBProxy(url: string): Promise<any> {
			const response = await fetch(`${serverUrl}/api/tmdb`, {
				method: "POST",
				headers: createHeaders(localStorage.getItem("token")),
				body: JSON.stringify({ url }),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			return await response.json();
		}

		async function fetchTMDBData(
			animeName: string,
			isMovie: boolean = false,
		): Promise<TMDBData> {
			try {
				const searchUrl = isMovie
					? `https://api.themoviedb.org/3/search/movie?{api_key_tmdb}&query=${encodeURIComponent(animeName)}&language=fr-FR`
					: `https://api.themoviedb.org/3/search/tv?{api_key_tmdb}&query=${encodeURIComponent(animeName)}&language=fr-FR`;

				const searchData = await callTMDBProxy(searchUrl);

				let allAnimeData: TMDBSearchResult[] =
					searchData?.results?.filter((result: TMDBSearchResult) =>
						result.genre_ids?.includes(16),
					) || [];

				if (allAnimeData.length === 0) {
					allAnimeData = searchData?.results || [];
				}

				if (allAnimeData.length === 0) {
					const englishSearchUrl = isMovie
						? `https://api.themoviedb.org/3/search/movie?{api_key_tmdb}&query=${encodeURIComponent(animeName)}&language=en-US`
						: `https://api.themoviedb.org/3/search/tv?{api_key_tmdb}&query=${encodeURIComponent(animeName)}&language=en-US`;

					const englishSearchData =
						await callTMDBProxy(englishSearchUrl);
					allAnimeData = englishSearchData?.results || [];
				}

				if (allAnimeData.length === 0) {
					const searchVariations = [];

					const withoutPunctuation = animeName
						.replace(/[^\w\s]/g, "")
						.trim();
					if (withoutPunctuation !== animeName) {
						searchVariations.push(withoutPunctuation);
					}

					const words = animeName.split(/\s+/);
					for (let i = 1; i <= Math.min(3, words.length); i++) {
						const shortVersion = words.slice(0, i).join(" ");
						if (
							shortVersion !== animeName &&
							!searchVariations.includes(shortVersion)
						) {
							searchVariations.push(shortVersion);
						}
					}

					const wordsToTry = animeName
						.split(/\s+/)
						.filter(
							(word) =>
								![
									"ga",
									"wo",
									"ni",
									"no",
									"wa",
									"de",
									"to",
									"!",
									"?",
								].includes(word.toLowerCase()),
						);
					if (
						wordsToTry.length > 0 &&
						wordsToTry.join(" ") !== animeName
					) {
						searchVariations.push(wordsToTry.join(" "));
					}

					for (const variation of searchVariations) {
						const variationUrl = isMovie
							? `https://api.themoviedb.org/3/search/movie?{api_key_tmdb}&query=${encodeURIComponent(variation)}&language=en-US`
							: `https://api.themoviedb.org/3/search/tv?{api_key_tmdb}&query=${encodeURIComponent(variation)}&language=en-US`;

						try {
							const variationData =
								await callTMDBProxy(variationUrl);
							const variationResults =
								variationData?.results || [];

							if (variationResults.length > 0) {
								allAnimeData = variationResults;
								break;
							}
						} catch (error) {
							console.warn(
								`Error with variation "${variation}":`,
								error,
							);
						}
					}
				}

				if (allAnimeData.length === 0) {
					const firstWord = animeName.split(/\s+/)[0];
					if (firstWord.length > 2) {
						console.log(
							`Last attempt with first word: "${firstWord}"`,
						);
						const lastAttemptUrl = `https://api.themoviedb.org/3/search/tv?{api_key_tmdb}&query=${encodeURIComponent(firstWord)}&language=en-US`;

						try {
							const lastAttemptData =
								await callTMDBProxy(lastAttemptUrl);
							const lastAttemptResults =
								lastAttemptData?.results || [];

							const possibleAnimes = lastAttemptResults.filter(
								(result: TMDBSearchResult) => {
									const name = (
										result.name || ""
									).toLowerCase();
									const originalName = (
										result.original_name || ""
									).toLowerCase();

									return (
										result.genre_ids?.includes(16) ||
										name.includes("anime") ||
										originalName.includes("anime") ||
										result.genre_ids?.includes(10759) ||
										result.genre_ids?.includes(10765)
									);
								},
							);

							if (possibleAnimes.length > 0) {
								allAnimeData = possibleAnimes;
							}
						} catch (error) {
							console.warn(
								`Error with last attempt search:`,
								error,
							);
						}
					}
				}

				if (allAnimeData.length === 0) {
					return {
						title: "",
						overview: "Aucune information disponible sur TMDB",
						poster_path: "",
						vote_average: 0,
						first_air_date: "",
						logos: [],
						backdrops: [],
						posters: [],
						original_name: null,
					};
				}

				const calculateSimilarity = (
					str1: string,
					str2: string,
				): number => {
					const s1 = str1.toLowerCase().trim();
					const s2 = str2.toLowerCase().trim();

					if (s1 === s2) return 100;

					if (s1.includes(s2) || s2.includes(s1)) return 80;

					const normalize = (str: string) =>
						str
							.replace(/[^\w\s]/g, "")
							.replace(/\s+/g, " ")
							.trim();
					const n1 = normalize(s1);
					const n2 = normalize(s2);

					if (n1 === n2) return 95;
					if (n1.includes(n2) || n2.includes(n1)) return 75;

					const levenshteinDistance = (
						a: string,
						b: string,
					): number => {
						const matrix = Array(b.length + 1)
							.fill(null)
							.map(() => Array(a.length + 1).fill(null));
						for (let i = 0; i <= a.length; i++) matrix[0][i] = i;
						for (let j = 0; j <= b.length; j++) matrix[j][0] = j;
						for (let j = 1; j <= b.length; j++) {
							for (let i = 1; i <= a.length; i++) {
								matrix[j][i] =
									b[j - 1] === a[i - 1]
										? matrix[j - 1][i - 1]
										: Math.min(
												matrix[j - 1][i - 1] + 1,
												matrix[j][i - 1] + 1,
												matrix[j - 1][i] + 1,
											);
							}
						}
						return matrix[b.length][a.length];
					};

					const distance = levenshteinDistance(s1, s2);
					const maxLength = Math.max(s1.length, s2.length);
					return maxLength === 0
						? 0
						: ((maxLength - distance) / maxLength) * 100;
				};

				const animeScores = allAnimeData.map((anime, index) => {
					const tmdbName = anime[isMovie ? "title" : "name"] || "";
					const originalName = anime.original_name || "";
					const titleScore = calculateSimilarity(animeName, tmdbName);
					const originalScore = originalName
						? calculateSimilarity(animeName, originalName)
						: 0;
					const popularityBonus = Math.min(
						(anime.popularity || 0) / 100,
						10,
					);
					const voteBonus = Math.min(
						(anime.vote_count || 0) / 100,
						5,
					);
					const finalScore =
						Math.max(titleScore, originalScore) +
						popularityBonus +
						voteBonus;

					return {
						index,
						score: finalScore,
						anime,
						titleScore,
						originalScore,
						tmdbName,
						originalName,
					};
				});

				animeScores.sort((a, b) => b.score - a.score);
				const bestMatch = animeScores[0]?.anime;
				const animeId = bestMatch?.id;

				if (!animeId) {
					throw new Error("No anime ID found in TMDB results");
				}

				let imageData = null;
				try {
					const imageUrl = `https://api.themoviedb.org/3/${isMovie ? "movie" : "tv"}/${animeId}/images?{api_key_tmdb}&include_image_language=ja,en,null`;
					imageData = await callTMDBProxy(imageUrl);

					if (!imageData?.logos?.length) {
						const fallbackUrl = `https://api.themoviedb.org/3/${isMovie ? "movie" : "tv"}/${animeId}/images?{api_key_tmdb}`;
						imageData = await callTMDBProxy(fallbackUrl);
					}
				} catch (imageError) {
					console.warn(
						"Error fetching images from TMDB:",
						imageError,
					);
					imageData = { logos: [], backdrops: [] };
				}

				return {
					title: bestMatch.title || bestMatch.name,
					overview: bestMatch.overview,
					poster_path: bestMatch.poster_path,
					vote_average: bestMatch.vote_average,
					first_air_date:
						bestMatch.first_air_date || bestMatch.release_date,
					popularity: bestMatch.popularity,
					vote_count: bestMatch.vote_count,
					logos: imageData?.logos || [],
					backdrops: imageData?.backdrops || [],
					posters: imageData?.posters || [],
					original_name: bestMatch.original_name || null,
				};
			} catch (error) {
				console.error("Error fetching TMDB data:", error);
				throw error;
			}
		}

		return await fetchTMDBData(id, isMovie);
	};

	function get_progress() {
		return new Promise((resolve, reject) => {
			fetch(serverUrl + "/api/get_progress", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: localStorage.getItem("token") || "",
				},
				body: JSON.stringify({ id: anime.id, idUser: menu.user.id }),
			})
				.then((response) => {
					return response.json();
				})
				.then((data) => {
					console.log(data);
					resolve(data);
				})
				.catch((error) => {
					console.warn(error);
				});
		});
	}

	fetch(serverUrl + "/api/get_anime_season", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Authorization: localStorage.getItem("token") || "",
		},
		body: JSON.stringify({ url: anime.url, serverUrl: serverUrl }),
	})
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			get_progress().then((progress) => {
				progressData = progress;
			});
			let season = data.season;
			let isMovie = false;

			if (anime?.genre.includes("Vf")) {
				data.season.forEach((element: Season) => {
					season.push({
						name: element.name,
						url: element.url,
						lang: "vf",
					});
				});
			}
			allSeasons = season;
			isMovie = season[0]?.name.toLowerCase().includes("film");
			get_data_from_tmdb(anime.title, isMovie).then((data) => {
				if (!data) {
					imageLoaded = true;
					dataFromTmdb.fetch = true;
				} else {
					const logoData = (data?.logos ?? [])[0];
					const backdropData = (data?.backdrops ?? [])[0];

					if (logoData) logoImg = base_url_tmdb + logoData.file_path;
					if (backdropData)
						backgroundImg = base_url_tmdb + backdropData.file_path;
					
					dataFromTmdb = {
						...dataFromTmdb,
						title: data.title || anime.title,
						firstAirDate: data.first_air_date || "",
						overview: data.overview || "Aucune description disponible",
						popularity: data.popularity || 0,
						note: data.vote_average || 0,
						nbVotes: data.vote_count || 0,
						fetch: true
					};
					
					getAverageColor(
						backgroundImg ? backgroundImg : anime.img,
						(color: any) => {
							if (menu.selected !== 3) return;
							dominantColor = `rgb(${Math.abs(color[0] - 40)}, ${Math.abs(color[1] - 40)}, ${Math.abs(color[2] - 40)})`;
							menu.dominantColor = dominantColor;
						},
					);
				}
			}).catch((error) => {
				imageLoaded = true;
				dataFromTmdb.fetch = true;
				console.warn("TMDB error:", error);
			});
		})
		.catch((error) => {
			console.warn(error);
		});

	function getAverageColor(imageSrc: string, callback: Function) {
		fetch(serverUrl + "/api/get_average_color", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: localStorage.getItem("token") || "",
			},
			body: JSON.stringify({ url: imageSrc }),
		})
			.then((response) => {
				return response.json();
			})
			.then((data) => {
				callback(data.average_color);
			})
			.catch((error) => {
				console.warn(error);
			});
	}
</script>

<main class={animation ? "" : "animation-hide"}>
	<div class="bg-container">
		<div class="linear-gradient"></div>
		<img
			src={anime.img}
			alt={menu.data.title}
			class="{imageLoaded && !dataFromTmdb.noData
				? 'hideBg'
				: 'bg'} {animation ? 'animation-show' : ''}"
			style="z-index: 2;"
		/>
		<img
			src={backgroundImg}
			alt={menu.data.title}
			class="bg {animation ? 'animation-show' : ''}"
			on:load={() => {
				imageLoaded = true;
			}}
		/>
	</div>
	{#if imageLoaded && dataFromTmdb.fetch}
		<div class="left">
			{#if logoImg}
				<img src={logoImg} alt={menu.data.title} />
			{/if}
			<h1>{anime.title}</h1>
			<p class="genre" style="text-align: center;">
				{genreString.join(", ")}
			</p>
			{#if logoImg}
				<div class="line" style="border-top: 1px solid #fff;">
					<p class="type">Date de sortie</p>
					<p>
						{new Date(
							dataFromTmdb.firstAirDate,
						).toLocaleDateString()}
					</p>
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
		<div class="bg-button">
			<button
				class="see-button"
				on:click={() => {
					menu.data = {
						anime: {
							...menu.data,
							season: allSeasons,
							progress: progressData,
						},
						tmdb: dataFromTmdb,
					};
					animation = false;
					setTimeout(() => {
						menu.selected = 4;
						navigate("/player", { replace: true });
					}, 500);
				}}>{progressData.find ? "Reprendre" : "Regarder"}</button
			>
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
		opacity: 1;
	}
	.animation-show {
		animation: showBgAnime 0.5s;
	}
	.animation-hide {
		animation: hide-main 0.5s;
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
		background: linear-gradient(
			90deg,
			rgba(51, 51, 51, 1) 0%,
			rgba(51, 51, 51, 1) 1%,
			rgba(51, 51, 51, 0.4) 50%,
			rgba(0, 0, 0, 0) 100%
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
		overflow-y: auto;
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
		background: linear-gradient(
			90deg,
			#333,
			#666,
			#999,
			#ccc,
			#999,
			#666,
			#333
		);
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
	@keyframes hide-main {
		0% {
			opacity: 1;
			transform: translateX(0%);
		}
		100% {
			opacity: 0;
			transform: translateX(-10%);
		}
	}
</style>
