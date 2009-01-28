<%@ page contentType="text/html; charset=UTF-8" %>

<%-- script level app-specific includes here --%>

	<%-- this is an example of an application specific style sheet  --%>
   <link rel="stylesheet" type="text/css" href="my_styles.css" />

<%-- appending this ensures that the script is reloaded whenever it changes, by preventing
     caching - useful for development--%>
<% String r = "?r=" + System.currentTimeMillis(); %>

	<!--  note: handlers.js should be last in the list, since it defines a global list of 
	      handlers which may refer to functions defined elsewhere -->
	<script type="text/javascript">
      document.domain="localhost";
    </script>
	<script src="handlers.js<%=r%>"></script> 