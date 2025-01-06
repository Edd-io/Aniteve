import { writable } from 'svelte/store';

class Downloader {
	request = indexedDB.open("fileStore", 1);
	listWritable = writable([] as any);
	list = [];
	inProgress = false;
	wasDownloaded = [];
	db = null;

	constructor()
	{
		const thisClass = this;

		this.request.onupgradeneeded = (event: any) =>{
            const db = event.target.result;
            if (!db.objectStoreNames.contains('downloads')) {
                const store = db.createObjectStore('downloads', { keyPath: 'id', autoIncrement: true });
                store.createIndex('fileName', 'fileName', { unique: true });
            }
        };

		this.request.onsuccess = (event: any) => {
			thisClass.db = event.target.result;
		}




		this.listWritable.subscribe((list) => {
			if (list.length === 0)
				return;
			thisClass.list.push(list[0] as never);
			thisClass.listWritable.update((list) => {
				list.shift();
				return (list);
			});
			if (this.inProgress)
			{
				console.log('Add to queue');
				return;
			}
			thisClass.inProgress = true;
			this.downloadEpisode();
		});
	}

	addNewDownload(data: any)
	{
		this.listWritable.update((list) => {
			list.push(data);
			return (list);
		});
	}

	async downloadEpisode()
	{
		while (1)
		{
			console.log("Download " + this.list[0].title + " Episode " + this.list[0].episode + " " + this.list[0].season);
			console.log("src: " + this.list[0].src);
			if (this.list[0].src.includes('.mp4'))
			{
				const response = await fetch(this.list[0].src);
				const blob = await response.blob();
				// save in indexedDB
			}
			console.log("end download");
			this.wasDownloaded.push(this.list[0]);
			this.list.shift();
			if (this.list.length === 0)
			{
				this.inProgress = false;
				break;
			}
		}
	}

}

const downloader = new Downloader();

export default downloader;