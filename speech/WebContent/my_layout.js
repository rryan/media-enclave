function layoutHandler(frameWidth, frameHeight, top, left) {
  //Any app-specific layout goes here, you should be prepared to resize any part of your app
  //on application intialization and when the window is resized
  
  
  //In the tic-tac-toe example application, this isn't really necessary, but we do it
  //anyway do show how it works.  We dynamically set the size of the MainDiv defined
  //in body_includes.jsp so that it always fits in the "main" window area
  
  //example of position a div: we put the MainDiv in the "main" window 
  var mainTop = top;
  var mainWidth = frameWidth - 5;
  var mainLeft = 0;
  var mainHeight = frameHeight - top;
  
  var mainE = document.getElementById("MainDiv");
  if(mainE) {
  	mainE.style.left = mainLeft + "px";
  	mainE.style.top = mainTop + "px";
  	mainE.style.width = mainWidth + "px";
  	mainE.style.height = mainHeight + "px";
  }
}