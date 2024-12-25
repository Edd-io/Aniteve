class GetSourceFile
{
	static from(url)
	{
		if (url.startsWith("https://video.sibnet.ru/"))
		{
			console.log("Sibnet url");
			return (this.fromSibnet(url));
		}
	}

	static fromSibnet(url)
	{
		return (new Promise((resolve, error) => {
			fetch(url).then(response => response.text())
			.then((content) => {
				const	endPos = content.indexOf('.mp4"') + 4;
				let		startPos = endPos - 1;

				while (startPos > 0 && content[startPos] != '"')
					startPos--;
				const url1 = "http://localhost:8080/sibnet" + content.slice(startPos + 1, endPos);
				const url2 = "https://video.sibnet.ru" + content.slice(startPos + 1, endPos);
				resolve([url1, url2]);
			})
			.catch((err) => {
				console.warn(err);
				error();
			});
		}));
	}
}

export {GetSourceFile};
// module.exports = GetSourceFile;