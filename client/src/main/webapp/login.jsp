<%-- === Use WRO4J plugin when you want to switch between pre-compiled and dynamic resources === --%>
<%-- === when running Jetty or Tomcat Maven plugins or a WAR file                            === --%>
<%--<%@ taglib prefix="wro" uri="/twigkit/wro" %>--%>


<!DOCTYPE html>
<%@ page contentType="text/html" pageEncoding="UTF-8" %>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Enterprise Search</title>
    <meta name="description" content="">
    <meta name="author" content="Twigkit">
    <meta name="viewport" content="minimal-ui, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, width=440">

    <%-- === Use WRO4J plugin when you want to switch between pre-compiled and dynamic resources === --%>
    <%-- === when running Jetty or Tomcat Maven plugins or a WAR file                            === --%>
    <%--<link rel="stylesheet" href="${wro:resourcePath('main.css', pageContext.request)}">--%>

	<%-- Comment this out if you use the WRO4J plugin above --%>
    <link rel="stylesheet" type="text/css" href="${pageContext.request.contextPath}/wro/css/main.css" />

    <link rel="stylesheet" href="${pageContext.request.contextPath}/assets/login.css">
    <!--[if lt IE 9]>
    <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
</head>

<body class="login" ng-app="appkitApp">

<div class="login-content">

    <widget:login-form
            method="POST"
            action="${pageContext.request.contextPath}/j_spring_security_check"
            append-hash-to-action="true"
            branding-class="branding"
            logo="${pageContext.request.contextPath}/assets/squarelogo.png"
            logo-width="65"
            title="Enterprise Search"
            title-element="h1"
            username-class="field required field-email"
            username-label="Username"
            password-class="field required field-password"
            password-label="Password"
            remember="false"
    ></widget:login-form>

</div>

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
