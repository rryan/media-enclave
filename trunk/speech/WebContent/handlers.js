// cross-server thingy
document.domain = "localhost";

// functions for interacting with the backend

// definitions of callbacks from the "generic" portion
var _wamiHandlers = new Object();
_wamiHandlers.responseHandler = handleResponse;
_wamiHandlers.audioConnectedHandler = null;
_wamiHandlers.layoutHandler = layoutHandler;
_wamiHandlers.onLoadHandler = onLoadHandler;
_wamiHandlers.onUnloadHandler = null;
_wamiHandlers.pollExceptionHandler = null;

function onLoadHandler() {
	// any onload handling here
}

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
		if (replyType == "search") {
			search(replyNode);
		}
		if (replyType == "queue") {
			queue(replyNode);
		}
		if (replyType == "dequeue") {
			dequeue(replyNode);
		}
		if (replyType == "pause") {
			pause(replyNode);
		}
		if (replyType == "resume") {
			resume(replyNode);
		}
		if (replyType == "dequeueall") {
			dequeueall(replyNode);
		}
		if (replyType == "playlist") {
			playlist(replyNode);
		}
	} catch (e) {
		alert(e);
	}
}

function queue(replyNode) {
	var id = replyNode.getAttribute("id");
	var ifr = document.getElementById("iframe");
	ifr.setAttribute("src", "http://localhost:8000/audio/queue/?ids=" + id);
}

function playlist(replyNode) {
	var pid = replyNode.getAttribute("pid");
	var ifr = document.getElementById("iframe");
	ifr.setAttribute("src", "http://localhost:8000/audio/playlists/normal/" + pid + "/");
	setTimeout('playlist_finish()', 2000);
}

function playlist_finish() {
	box = window.frames["aenclave"].document.getElementById("checkall");
	box.checked = true;
	window.frames["aenclave"].window.songlist.select_all(box);
	window.frames["aenclave"].window.songlist.queue();
}

function dequeue(replyNode) {
	//var ifr = document.getElementById("iframe");
	//alert("attempting skip...");
	window.frames["aenclave"].window.controls.skip();
	//ifr.window.controls.skip();  //err...no
	//alert("after skip.");
}

function dequeueall(replyNode) {
	//alert("attempting dequeue all...");
	//check whether on channels page; navigate there if not
	if (window.frames["aenclave"].window.location.pathname != "/audio/channels/") {
		var ifr = document.getElementById("iframe");
		ifr.setAttribute("src", "http://localhost:8000/audio/channels/");
		setTimeout('dequeueall_finish()', 2000);
	}
	else {
		dequeueall_finish();
	}
}

function dequeueall_finish() {
	//alert('waited');
	box = window.frames["aenclave"].document.getElementById("checkall");
	box.checked = true;
	window.frames["aenclave"].window.songlist.select_all(box);
	//alert("after select all");
	window.frames["aenclave"].window.channels.dequeue();
	//dequeue the currently playing song
	window.frames["aenclave"].window.controls.skip();
	//alert("after dequeue all");
}

//defunct as of now
function search(replyNode) {
	var qr = replyNode.getAttribute("query");
	var ifr = document.getElementById("iframe");
	ifr.setAttribute("src", "http://localhost:8000/audio/search/?q=" + qr);
	
}

function pause(replyNode) {
	window.frames["aenclave"].window.controls.pause();
}

function resume(replyNode) {
	window.frames["aenclave"].window.controls.play();
}

function layoutHandler(frameWidth, frameHeight, top, left) {
	// Any app-specific layout goes here, you should be prepared to resize any
	// part of your app
	// on application intialization and when the window is resized

	// example of position a div: we put the MainDiv in the "main" window
	var mainTop = top;
	var mainWidth = frameWidth - 5;
	var mainLeft = 0;
	var mainHeight = frameHeight - top;

	var mainE = document.getElementById("MainDiv");
	if (mainE) {
		mainE.style.left = mainLeft + "px";
		mainE.style.top = mainTop + "px";
		mainE.style.width = mainWidth + "px";
		mainE.style.height = mainHeight + "px";
	}
}