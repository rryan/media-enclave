/*
Functions for interacting with the server

this library code assumes a global variable called _wamiHandlers which should
be set by anyone using the library.  It allows points of override to the
default functionality

Definitions:
_wamiHandlers.responseHandler(replyNode)
		REQUIRED: This handles the XML messages sent from the server
_wamiHandlers.onLoadHandler
		Called at the beginning of onLoad
_wamiHandlers.onUnloadHandler
		Called at the beginning of onUnLoad
_wamiHandlers.pollExceptionHandler(e)
		Called when an exception occurs within polling galaxy
_wamiHandlers.responseExceptionHandler(e) 
		Called when an exception occurs within handleResponse
_wamiHandlers.audioConnectedHandler
		Called after the audio has been connected, but before polling begins
_wamiHandlers.layoutHandler(frameWidth, frameHeight, top, left)
        Do any necessary layout of your components during load or resize
 */

/* Globally available variables */
var _stopPolling = false;

function onResize() {
	doLayout();
}

function onLoad() {
	if (_wamiHandlers && _wamiHandlers.onLoadHandler)
		_wamiHandlers.onLoadHandler();

	connectAudio();

	if (!_stopPolling) {
		setTimeout("poll()", 5);
	}
}

function onUnload() {
	if (_wamiHandlers && _wamiHandlers.onUnloadHandler)
		_wamiHandlers.onUnloadHandler();
}

function onBeforeUnload() {
	if (_wamiHandlers && _wamiHandlers.onBeforeUnloadHandler)
		_wamiHandlers.onBeforeUnloadHandler();
}

/**
 * post an xml data to the controller, second argument controls asynchronicity
 * 
 */
function postXML(message, isAsynchronous) {
	if (isAsynchronous == null) {
		isAsynchronous = true;
	}

	var request = newXMLRequest();
	request.open('POST', "ajaxcontrol", isAsynchronous);
	request.setRequestHeader("Content-Type", "text/xml");
	request.send(message);
}

function poll() {
	if (_stopPolling) {
		return;
	}

	var request = newXMLRequest();
	request.open('POST', "ajaxcontrol", true);
	request.setRequestHeader("Content-Type", "text/xml");
	request.onreadystatechange = function() {
		try {
			if (request.readyState == 4) {
				if (request.status == 200) {
					var nodeList = request.responseXML
							.getElementsByTagName('reply');
					if (nodeList == null || nodeList.length == 0) {
						alert("Bad XML:\n" + request.responseText);
						stopPolling();
					}

					for ( var i = 0; i < nodeList.length; i++) {
						var replyNode = nodeList[i];
						try {
							if (replyNode.getAttribute("type") == "timeout") {
								if (_wamiHandlers
										&& _wamiHandlers.timeoutHandler)
									_wamiHandlers.timeoutHandler();
								else
									genericTimeoutHandler();
							}

							if (_wamiHandlers && _wamiHandlers.responseHandler)
								_wamiHandlers.responseHandler(replyNode);
							else
								alert("ERROR: You MUST define _wamiHandlers.responseHandler or you will have no functionality");
						} catch (e) {
							if (_wamiHandlers
									&& _wamiHandlers.responseExceptionHandler) {
								_wamiHandlers.responseExceptionHandler(e);
							}
						}
					}
					if (!_stopPolling) {
						poll();
					}
				} else {
					var html = "<br /><br /><br /><br />Bad server status ("
							+ request.status
							+ ").  Click OK to reload the page.  If that doesn't work, contact the system administrator";

					var popup = createHtmlWindow(html, "GenericPopupWindow",
							"Popup");
				}
			}
		} catch (e) {
			// we usually get an exception on page exit,
			// just catch it and end gracefully
			if (_wamiHandlers && _wamiHandlers.pollExceptionHandler)
				_wamiHandlers.pollExceptionHandler(e);
		}
	};

	request
			.send("<?xml version='1.0' encoding='UTF-8'?><update polling='true' />");
}

function genericTimeoutHandler() {
	window.location.href = "generic/components/timeout.jsp";
}

function connectAudio() {
	if (_wamiHandlers && _wamiHandlers.audioConnectedHandler)
		_wamiHandlers.audioConnectedHandler();
}

function stopPolling() {
	_stopPolling = true;
}

function doLayout() {
	var dim = getFrameDimensions();

	if (dim == null || dim.frameWidth == -1 || dim.frameHeight == -1) {
		return;
	}

	var frameWidth = dim.frameWidth;
	var frameHeight = dim.frameHeight;

	var appletE = document.getElementById("AppletDiv");
	var statusE = document.getElementById("StatusBar");
	var logoE = document.getElementById("Logo");

	var statusHeight = 19;
	var statusWidth = frameWidth / 3;

	var appletWidth = (appletE != null) ? _appletWidth : 0;
	var appletHeight = (appletE != null) ? _appletHeight : 0;
	var logoHeight = (logoE != null) ? _logoImgHeight : 0;
	var logoWidth = (logoE != null) ? _logoImgWidth : 0;

	var topHeight = (logoHeight > appletHeight) ? logoHeight : appletHeight;

	//if (appletE) {
		//appletE.style.position = "absolute";
		//appletE.style.top = "0px";
		//appletE.style.left = logoWidth + 5 + "px";
		//appletE.style.width = appletWidth + "px";
		//appletE.style.height = appletHeight;
	//}

	if (appletE) {
		layoutHelperE = document.getElementById("AudioLayoutHelper");
		layoutHelperE.style.left = logoWidth + 5 + appletWidth + "px";
		layoutHelperE.style.top = "0px";
	}

	if (logoE) {
		logoE.style.top = ((topHeight - logoHeight) / 2) + "px";
		logoE.style.left = "0px";
		logoE.style.width = logoWidth + "px";
		logoE.style.height = logoHeight + "px";
	}

	// let any application-specific handlers do their layout
	if (_wamiHandlers && _wamiHandlers.layoutHandler)
		_wamiHandlers.layoutHandler(frameWidth, frameHeight, topHeight, 0);
}
