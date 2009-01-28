// cross-server thingy
document.domain = "localhost";

// functions for interacting with the backend

// definitions of callbacks from the "generic" portion
var _wamiHandlers = {
	responseHandler: handleResponse,
	audioConnectedHandler: null,
	layoutHandler: layoutHandler,
	onLoadHandler: onLoadHandler,
	onUnloadHandler: null,
	pollExceptionHandler: null
};

function onLoadHandler() {
	// any onload handling here
}

function layoutHandler(frameWidth, frameHeight, top, left) {
	// Any app-specific layout goes here, you should be prepared to resize any
	// part of your app on application intialization and when the window is
	// resized.
}

// Response callbacks for various reply types.
var responseHandlers = {
	search: search,
	queue: queue,
	dequeue: dequeue,
	pause: pause,
	resume: resume,
	dequeueall: dequeueall,
	playlist: playlist,
	tellsongname: tellsongname
};

/**
 * replyNode will look like this: <reply type="TYPE"> ANY_VALID_XML </reply>.
 * 
 * When sent from the server, this should be a list, e.g.: <replies> <reply
 * type="TYPE1" ... /> <reply type="TYPE2" ../> </replies> But we get them one
 * by one in this function
 */
function handleResponse(replyNode) {
	try {
		var replyType = replyNode.getAttribute("type");
		responseHandlers[replyType](replyNode);
	} catch (e) {
		alert(e);
	}
}

function setAenclaveSrc(url) {
	var frame = window.top.document.getElementById('aenclave');
	frame.src = url;
}

function aenclaveWindow() {
	return window.top.frames.aenclave.window;
}

function queue(replyNode) {
	var id = replyNode.getAttribute("id");
	setAenclaveSrc("http://localhost:8000/audio/queue/?ids=" + id);
}

function playlist(replyNode) {
	var pid = replyNode.getAttribute("pid");
	setAenclaveSrc("http://localhost:8000/audio/playlists/normal/" + pid + "/");
	setTimeout('playlist_finish()', 2000);
}

function playlist_finish() {
	var aenclave = aenclaveWindow();
	var box = aenclave.document.getElementById("checkall");
	box.checked = true;
	aenclave.songlist.select_all(box);
	aenclave.songlist.queue();
}

function dequeue(replyNode) {
	aenclaveWindow().controls.skip();
}

function dequeueall(replyNode) {
	//alert("attempting dequeue all...");
	//check whether on channels page; navigate there if not
	if (aenclaveWindow().location.pathname != "/audio/channels/") {
		setAenclaveSrc("http://localhost:8000/audio/channels/");
		setTimeout('dequeueall_finish()', 2000);
	}
	else {
		dequeueall_finish();
	}
}

function dequeueall_finish() {
	//alert('waited');
	var box = aenclaveWindow().document.getElementById("checkall");
	box.checked = true;
	aenclaveWindow().songlist.select_all(box);
	//alert("after select all");
	aenclaveWindow().channels.dequeue();
	//dequeue the currently playing song
	aenclaveWindow().controls.skip();
	//alert("after dequeue all");
}

//defunct as of now
function search(replyNode) {
	var qr = replyNode.getAttribute("query");
	setAenclaveSrc("http://localhost:8000/audio/search/?q=" + qr);
}

function pause(replyNode) {
	aenclaveWindow().controls.pause();
}

function resume(replyNode) {
	aenclaveWindow().controls.play();
}

function tellsongname(replyNode) {
	var tts = document.getElementById("tts");
	var url = "http://wami.csail.mit.edu:8080/synthesizers/synthesize?language=english&synth_string=";
	text = replyNode.getAttribute("songname");
	info = aenclaveWindow().controls.playlist_info.songs[0];
	if (info != null) {
		//replace hyphen with 'by'
		info = info.replace(" - ", " by ").toLowerCase();
		//and append to tts
		text += info;
	}
	url = url + text;
	tts.setAttribute("src", url);
}
