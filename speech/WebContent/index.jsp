<!--  we just forward to the generic, note that the generic has several callbacks we implement in jsp_includes-->

<jsp:forward page="generic/main.jsp">
	<jsp:param name="originalRequestUrl" value="<%=request.getRequestURL().toString()%>" />
	<jsp:param name="contactEmail" value="youremailhere@domain.com" />
</jsp:forward>

