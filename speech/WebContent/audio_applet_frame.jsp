<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ page import="edu.mit.csail.sls.wami.WamiConfig"%>

<jsp:include page="initialize.jsp" />

<%
	if (request.getAttribute("forward") != null) {
		String forwardPage = (String) request.getAttribute("forward");
%>
<jsp:forward page="<%=forwardPage%>" />
<%
	}
%>

<html xmlns="http://www.w3.org/1999/xhtml"
    xmlns:v="urn:schemas-microsoft-com:vml">

  <head>
    <%
      WamiConfig ac = WamiConfig.getConfiguration(getServletContext());

      if (ac.getUseAudio(request)) {
        String playUrl = ac.audioServletURL(request);
        String recordUrl = ac.recordServletURL(request);
        System.out.println("PLAY URL: " + playUrl);
        System.out.println("RECORD URL: " + recordUrl);
      }
    %>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />

    <title><%=ac.getTitle(request)%></title>

    <link rel="stylesheet" type="text/css" href="my_styles.css"/>

    <script language="JavaScript" type="text/javascript">
        var _info = navigator.userAgent;
        var _ns = false;
        var _ns6 = false;
        var _ie = (_info.indexOf("MSIE") > 0 &&
                   _info.indexOf("Win") > 0 &&
                   _info.indexOf("Windows 3.1") == -1);
        var _ie7 = (_info.indexOf("MSIE 7.") > 0);
        var _useSpeechDetector = <%=ac.getUseSpeechDetector(request)%>;
        var _logoImgWidth = <%=ac.getLogoWidth(request)%>;
        var _logoImgHeight = <%=ac.getLogoHeight(request)%>;
        var _logoSrc = "<%=ac.getLogo(request)%>";
        var _appletWidth = <%=ac.getAppletWidth(request)%>;
        var _appletHeight = <%=ac.getAppletHeight(request)%>;
        var _mobile = <%=ac.getMobile(request)%>;
        var _mobileWidth = <%=ac.getMobileWidth(request)%>;
        var _mobileHeight = <%=ac.getMobileHeight(request)%>;
        var _synthURL = "<%=ac.audioServletURL(request)%>";
        var _isPlaying = false;
    </script>

    <%
      //append current time in millis to all js, to ensure they get reloaded.
      //Mobile opera seems to not correctly reinitialize global variables
      //in non-freshly reloaded pages
      String r = "?r=" + System.currentTimeMillis();
    %>
	<script type="text/javascript">
      document.domain="localhost";
    </script>
	<script src="handlers.js<%=r%>"></script> 
    <script src="wami.js<%=r%>"></script>
    <script src="util.js<%=r%>"></script>
  </head>

  <body onload="onLoad()" onresize="onResize()" onunload="onUnload()">

    <jsp:include flush="true" page="audio_applet.jsp" />

    <%--<div id="reply-div"></div>--%>

    <iframe id="tts" name="tts" src="" width="1%" height="1%"
        style="position:absolute; left:-9999px;"> 
    </iframe>
    <script language="JavaScript" type="text/javascript">
      onResize();
    </script>

  </body>
</html>
