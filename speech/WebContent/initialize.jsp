<%@ page import="edu.mit.csail.sls.wami.WamiServlet"%>
<%@ page import="edu.mit.csail.sls.wami.WamiConfig"%>
<%@ page import="edu.mit.csail.sls.wami.relay.ReachedCapacityException"%>

<%
	WamiConfig ac = WamiConfig.getConfiguration(getServletContext());

	Boolean passedBoolean = (Boolean) session
			.getAttribute("passedBrowserTest");

	boolean failedBrowserTest = ac.getTestBrowser(request)
			&& (passedBoolean == null || !(passedBoolean != null && passedBoolean
					.booleanValue()));

	if (failedBrowserTest) {
		request.setAttribute("forward",
				"/generic/components/testbrowser/testbrowser.jsp");
	}

	if (ac.getUseRelay() && !failedBrowserTest) {
		try {
			WamiServlet.initializeRelay(request);
		} catch (ReachedCapacityException rce) {
			request.setAttribute("forward",
					"/generic/components/toomany.jsp");
			request.setAttribute("exception", rce);
		}
	}
%>
