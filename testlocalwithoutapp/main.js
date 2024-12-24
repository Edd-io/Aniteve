const GetSourceFile = require('../src/GetSourceFile');
const parseFileEpisode = require('../src/parseFileEpisode');

fetch('https://anime-sama.fr/catalogue/365-days-to-the-wedding/saison1/vostfr/episodes.js')
.then((response) => {
	if (!response.ok) {
		throw new Error(`Erreur HTTP : ${response.status}`);
	}
	return response.text();
})
.then((content) => {
	content = content.replaceAll('var ', "globalThis.")
	try {
		eval(content);
		const eps = parseFileEpisode();
		GetSourceFile.from(eps['eps1'][0])?.then((videoUrl) => {
			console.log(videoUrl);
		})
	} catch (e) {
		console.error('Erreur dans eval :', e);
	}
})
.catch((err) => console.warn('Erreur lors de la requête :', err));