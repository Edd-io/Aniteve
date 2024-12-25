function parseFileEpisode()
{
	let i = 1;
	let data = {};

	while (1)
	{
		if (!global['eps' + i])
		{
			console.log("Number eps :", i);
			break ;
		}
		for (let j = 1; j < global['eps' + i].length + 1; j++)
		{
			if (data['eps' + j] == undefined)
				data['eps' + j] = [];
			data['eps' + j].push(global['eps' + i][j - 1]);
		}
		i++;
	}
	return (data);
}

export {parseFileEpisode};
// module.exports = parseFileEpisode;
