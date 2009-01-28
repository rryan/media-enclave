<%@ page import="edu.mit.csail.sls.wami.WamiConfig"%>
<%
	WamiConfig wc = WamiConfig.getConfiguration(getServletContext());
	if (wc.getUseAudio(request)) {
		String visibility = wc.getAudioAppletVisible(request) ? "" : "visibility: hidden";
%>

<%-- Turns out jsp:plugin doesn't work for our needs as 
     it will not accept dynamic class names or archives. 
     It may also have some issues in producing the proper
     code for some browsers. --%>
<div id="AppletDiv" style="<%=visibility%>">
<%
	String playUrl = wc.audioServletURL(request) + "?poll=true";
		String recordUrl = wc.recordServletURL(request);
		String recordAudioFormat = wc.getRecordAudioFormat();
		int recordSampleRate = wc.getRecordSampleRate();
		boolean recordIsLittleEndian = wc.getRecordIsLittleEndian();

		boolean greenOnEnableInput = wc.getGreenOnEnableInput(request);
		String appletClassName = wc.getAudioAppletClass(request);
		String appletArchives = wc.getAppletArchives(request);
		int appletWidth = wc.getAppletWidth(request);
		int appletHeight = wc.getAppletHeight(request);
		String hubLocation = (String) session
				.getAttribute("hubLocationString");
		boolean useSpeechDetector = wc.getUseSpeechDetector(request);		
		String allowStopPlayingStr = request
				.getParameter("allowStopPlaying");
		boolean allowStopPlaying = allowStopPlayingStr == null
				|| "true".equalsIgnoreCase(allowStopPlayingStr);
		boolean playRecordTone = wc.getPlayRecordTone(request);
%> <!--"CONVERTED_APPLET"--> <!-- HTML CONVERTER --> <comment>
<script language="JavaScript" type="text/javascript"><!--
        var _ns = (navigator.appName.indexOf("Netscape") >= 0 && ((_info.indexOf("Win") > 0 && _info.indexOf("Win16") < 0 && java.lang.System.getProperty("os.version").indexOf("3.5") < 0) || (_info.indexOf("Sun") > 0) || (_info.indexOf("Linux") > 0) || (_info.indexOf("AIX") > 0) || (_info.indexOf("OS/2") > 0) || (_info.indexOf("IRIX") > 0)));
        var _ns6 = ((_ns == true) && (_info.indexOf("Mozilla/5") >= 0));
//--></script> </comment> <script language="JavaScript" type="text/javascript"><!--
    if (_ie == true) {
    	if(_ie7) {
		    document.writeln('<object classid="clsid:8AD9C840-044E-11D1-B3E9-00805F499D93" WIDTH = "<%=appletWidth%>" HEIGHT = "<%=appletHeight%>" NAME = "AudioApplet" ID = "AudioApplet" codebase="http://java.sun.com/update/1.5.0/jinstall-1_5-windows-i586.cab#Version=5,0,0,5"><xmp>');
    	} else {
			document.writeln('<object classid="clsid:8AD9C840-044E-11D1-B3E9-00805F499D93" WIDTH = "<%=appletWidth%>" HEIGHT = "<%=appletHeight%>" NAME = "AudioApplet" ID = "AudioApplet" codebase="http://java.sun.com/update/1.5.0/jinstall-1_5-windows-i586.cab#Version=5,0,0,5"><noembed><xmp>');
		}
    } else if (_ns == true && _ns6 == false) {
    	document.writeln('<embed ' +
	    'type="application/x-java-applet;version=1.5" \
            CODE = "<%=appletClassName%>" \
            ARCHIVE = "<%=appletArchives%>" \
            NAME = "AudioApplet" \
            WIDTH = "<%=appletWidth%>" \
            HEIGHT = "<%=appletHeight%>" \
	    	ID = "AudioApplet" \
            location ="<%=hubLocation%>" \
            useSpeechDetector = "<%=useSpeechDetector%>" \
  			httpOnly = "true" \
  			recordUrl = "<%=recordUrl%>" \
  			recordAudioFormat = "<%=recordAudioFormat%>" \
  			recordSampleRate = "<%=recordSampleRate%>" \
  			recordIsLittleEndian = "<%=recordIsLittleEndian%>" \
            layout ="stacked" \
            allowStopPlaying="<%=allowStopPlaying%>" \
            greenOnEnableInput="<%=greenOnEnableInput%>" \
            playUrl="<%=playUrl%>" \
            playRecordTone="<%=playRecordTone%>" \
            vision ="false" / ' +
 	    'scriptable=false ' +
	    'pluginspage="http://java.sun.com/products/plugin/index.html#download"><noembed><xmp>');
	}
//--></script> <applet CODE="<%=appletClassName%>" ARCHIVE="<%=appletArchives%>"
	WIDTH="<%=appletWidth%>" HEIGHT="<%=appletHeight%>" NAME="AudioApplet"
	ID="AudioApplet"></xmp>
	<PARAM NAME=CODE VALUE="<%=appletClassName%>">
	<PARAM NAME=ARCHIVE VALUE="<%=appletArchives%>">
	<PARAM NAME=NAME VALUE="AudioApplet">
	<param name="type" value="application/x-java-applet;version=1.5">
	<param name="scriptable" value="false">
	<PARAM NAME="location" VALUE="<%=hubLocation%>" />
	<PARAM NAME="useSpeechDetector" VALUE="<%=useSpeechDetector%>" />
	<PARAM NAME="vision" VALUE="false" />
	<PARAM NAME="layout" VALUE="stacked" />
	<PARAM NAME="playUrl" VALUE="<%=playUrl%>" />
	<PARAM NAME="httpOnly" VALUE="true" />
	<PARAM NAME="recordUrl" VALUE="<%=recordUrl%>" />
	<PARAM NAME="recordAudioFormat" VALUE="<%=recordAudioFormat%>" />
	<PARAM NAME="recordSampleRate" VALUE="<%=recordSampleRate%>" />
	<PARAM NAME="recordIsLittleEndian" VALUE="<%=recordIsLittleEndian%>" />
	<PARAM NAME="allowStopPlaying" VALUE="<%=allowStopPlaying%>" />
	<PARAM NAME="greenOnEnableInput" VALUE="<%=greenOnEnableInput%>" />
	<PARAM NAME="playRecordTone" VALUE="<%=playRecordTone%>" />	
</applet> <%
 	if (false /* never gets here on purpose! */) {
 %> <!-- This is here to keep eclipse from complaining the javascript above actually injects these  -->
<object> <embed>
	<noembed> <%
 	}
 %> </noembed>
	</embed> </object> <!--
<APPLET CODE = "<%=appletClassName%>" ARCHIVE = "<%=appletArchives%>" WIDTH = "<%=appletWidth%>" HEIGHT = "<%=appletHeight%>" NAME = "AudioApplet">
<PARAM NAME = "location" VALUE="<%=hubLocation%>" />
<PARAM NAME = "useSpeechDetector" VALUE="<%=useSpeechDetector%>" />
<PARAM NAME = "httpOnly" VALUE="true" />
<PARAM NAME= "recordUrl" VALUE="<%=recordUrl%>" />
<PARAM NAME= "recordAudioFormat" VALUE="<%=recordAudioFormat%>" />
<PARAM NAME= "recordSampleRate" VALUE="<%=recordSampleRate%>" />
<PARAM NAME= "recordIsLittleEndian" VALUE="<%=recordIsLittleEndian%>" />
<PARAM NAME = "vision" VALUE="false" />
<PARAM NAME = "layout" VALUE="stacked" />
<PARAM NAME = "allowStopPlaying" VALUE="<%=allowStopPlaying%>" />
<PARAM NAME="playUrl" VALUE="<%=playUrl%>" />
<PARAM NAME = "greenOnEnableInput" VALUE="<%=greenOnEnableInput%>" />
<PARAM NAME = "playRecordTone" VALUE="<%=playRecordTone%>" />
</APPLET>
--> <!--"END_CONVERTED_APPLET"--></div>
<%
	}
%>
<div id="AudioLayoutHelper" style="position: absolute; "></div>
