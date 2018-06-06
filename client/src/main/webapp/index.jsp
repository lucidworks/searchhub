<%-- === Use WRO4J plugin when you want to switch between pre-compiled and dynamic resources === --%>
<%-- === when running Jetty or Tomcat Maven plugins or a WAR file                            === --%>
<%--<%@ taglib prefix="wro" uri="/twigkit/wro" %>--%>

<!doctype html>
<html class="no-js">

<head>
    <base href="${pageContext.request.contextPath}/"/>
    <meta charset="utf-8">
    <title>Fusion Search</title>
    <meta name="description" content="">
    <meta name="viewport" content="width=device-width">

    <%-- === Use WRO4J plugin when you want to switch between pre-compiled and dynamic resources === --%>
    <%-- === when running Jetty or Tomcat Maven plugins or a WAR file                            === --%>
    <%--<link rel="stylesheet" href="${wro:resourcePath('main.css', pageContext.request)}">--%>

    <%-- Comment this out if you use the WRO4J plugin above --%>
    <link rel="stylesheet" type="text/css" href="${pageContext.request.contextPath}/wro/css/main.css" />
	

</head>

<body ng-app="appkitApp">

<!-- All views are loaded here -->
<ui-view autoscroll="true"></ui-view>

<div class="tk-stl-notifications"></div>


<%-- === Use WRO4J plugin when you want to switch between pre-compiled and dynamic resources === --%>
<%-- === when running Jetty or Tomcat Maven plugins or a WAR file                            === --%>
<%--<script src="${wro:resourcePath('vendor.js', pageContext.request)}" type="text/javascript"></script>--%>
<%--<script src="${wro:resourcePath('main.js', pageContext.request)}" type="text/javascript"></script>--%>

<%-- Comment this out if you use the WRO4J plugin above --%>
<script type="text/javascript" src="${pageContext.request.contextPath}/wro/js/vendor.js"></script>
<script type="text/javascript" src="${pageContext.request.contextPath}/wro/js/main.js"></script>


<script>
    angular.module('lightning').constant('contextPath', '${pageContext.request.contextPath}');
</script>

</body>
</html>