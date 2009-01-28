//really, really generic utilities

//alexgru: note 2007-11-09
//for Opera mobile 8.x on windows mobile,
//you must pass in a rootName for your xml document
//or you will be in trouble
function newXMLDocument(rootName) {
	if(rootName == null) {
		rootName = "";
	}
	//alert("newXMLDocument, rootName = '" + rootName + "'");
	if (document.implementation && document.implementation.createDocument) {
		return document.implementation.createDocument("",rootName,null);
	} else if (window.ActiveXObject) {
		var xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
		if(rootName != null) {
			xmlDoc.appendChild(xmlDoc.createElement(rootName));
		}
		return xmlDoc;
 	}

	// alert("ERROR: Your Browser Does Not Support The Creation of XML Documents");
	return null;
}



function newXMLRequest() {
	var xmlhttp=false;
	/*@cc_on @*/
	/*@if (@_jscript_version >= 5)
	// JScript gives us Conditional compilation, we can cope with old IE versions.
	// and security blocked creation of the objects.
 	try {
  		xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
 	} catch (e) {
  		try {
   		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
  	} catch (E) {
   		xmlhttp = false;
	  }
 	}
	@end @*/
	if (!xmlhttp && typeof XMLHttpRequest!='undefined') {
		try {
			xmlhttp = new XMLHttpRequest();
		} catch (e) {
			xmlhttp=false;
		}
	}
	if (!xmlhttp && window.createRequest) {
		try {
			xmlhttp = window.createRequest();
		} catch (e) {
			xmlhttp=false;
		}
	}

	return xmlhttp;
}

/**
 * copies attributes from src to dest, only copies attributes listed in the passed in array
 */
function copyAttributes(src, dest, attributes) {
	for(var i = 0; i < attributes.length; i++) {
		var attribute = attributes[i];
		var value = src.getAttribute(attribute);
		if(value) {
			dest.setAttribute(attribute, value);
		}
	}
}

/**
 * Returns the actual position of an element which has already been
 * positioned on the screen, as a rect with:
 * rect.top, rect.left, rect.width, rect.height
 */
function getBoundingRect(element) {
	var rect = new Object();
	if(document.getBoxObjectFor) {
		var box = document.getBoxObjectFor(element);
		rect.top = box.y;
		rect.left = box.x;
		rect.width = box.width;
		rect.height = box.height;
	} else if(element.getBoundingClientRect) {
		var r = element.getBoundingClientRect();
		rect.top = r.top;
		rect.left = r.left;
		rect.width = r.right - r.left;
		rect.height = r.bottom - r.top;
	} else if (element.offsetLeft) {
		// Safari is weird
		var elem = element;
		rect.top = elem.offsetTop;
		rect.left = elem.offsetLeft;
		rect.width = elem.offsetWidth;
		rect.height = elem.offsetHeight;
		
        // Start with the first offset parent
        elem = elem.offsetParent;

        // Stop at the body
        var body = document.body;

          // Border correction is only needed for each parent
          // not for the incoming element itself
        while (elem && elem != body)
        {
            // Add node offsets
            rect.left += elem.offsetLeft;
            rect.top += elem.offsetTop;

            // One level up (offset hierarchy)
            elem = elem.offsetParent;
        }
	}
	else {
		// Uncomment if you want to see some safari errors:
		//alert("bounding box not found");
	}
	
	return rect;
}

function getTarget(e) {
	var targ;
	if(e.target) targ = e.target;
	if(e.srcElement) targ = e.srcElement;
	if (targ.nodeType == 3) // safari bug
		targ = targ.parentNode;
		
	return targ;
}

function rectContains(rect, x, y) {	
	var value = (x >= rect.left && x <= rect.left + rect.width && y >= rect.top && y <= rect.top + rect.height);
	
	return value;
}

/**
  * helper functions for making window-type divs...doesn't do anything
  very fancy at the moment
 */

function createHtmlWindow(html, windowClassName, initialHelp) {
	var window = document.createElement("div");
	window.className = windowClassName;
	window.innerHTML = html;
	window.id = initialHelp;
	
	document.getElementsByTagName("body")[0].appendChild(window);
	return window;
}

function setCookie(cookieName, cookieValue, nDays) {
	var today = new Date();
	var expire = new Date();
	if (nDays==null || nDays==0) nDays=1;
	expire.setTime(today.getTime() + 3600000*24*nDays);
	document.cookie = cookieName+"="+escape(cookieValue)
	                + ";expires="+expire.toGMTString();
}


function getCookie(name) {	
	var start = document.cookie.indexOf( name + "=" );
	var len = start + name.length + 1;
	if ((!start) && (name != document.cookie.substring(0, name.length)))
	{
		return null;
	}
	if(start == -1) 
		return null;
	var end = document.cookie.indexOf( ";", len );
	if (end == -1) 
		end = document.cookie.length;
	return unescape( document.cookie.substring(len, end));
}

function getFrameDimensions() {
	var dimensions = new Object();
    //some cross platform junk
	if (self.innerWidth) {
		dimensions.frameWidth = self.innerWidth;
		dimensions.frameHeight = self.innerHeight;
	} else if (document.documentElement && document.documentElement.clientWidth) {
		dimensions.frameWidth = document.documentElement.clientWidth;
		dimensions.frameHeight = document.documentElement.clientHeight;
	} else if (document.body) {
		dimensions.frameWidth = document.body.clientWidth;
		dimensions.frameHeight = document.body.clientHeight;
	} else {
		dimensions.frameWidth = -1;
		dimensions.frameHeight = -1;
	}
	return dimensions;
}

//decide if we are on a small screen right now...
//the default definition is if the framewidth is less than
//800 pixels, but you can pass in your own maximum width
function isSmallScreen(thresholdWidth) {
	if(thresholdWidth == null) {
		thresholdWidth = 801;
	}

	var dim = getFrameDimensions();
	return(dim != null && dim.frameWidth != -1 && dim.frameWidth < thresholdWidth);
}


function clearChildren(e) {
	while(e.childNodes && e.childNodes.length > 0) {
		e.removeChild(e.childNodes[0]);
	}
}
