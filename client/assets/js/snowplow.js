;
(function (p, l, o, w, i, n, g) {
  if (!p[i]) {
    p.GlobalSnowplowNamespace = p.GlobalSnowplowNamespace || [];
    p.GlobalSnowplowNamespace.push(i);
    p[i] = function () {
      (p[i].q = p[i].q || []).push(arguments)
    };
    p[i].q = p[i].q || [];
    n = l.createElement(o);
    g = l.getElementsByTagName(o)[0];
    n.async = 1;
    n.src = w;
    g.parentNode.insertBefore(n, g)
  }
}(window, document, "script", "/assets/js/snowplow-local.js", "searchhub_snowplow"));

searchhub_snowplow("newTracker", "searchHub", location.hostname + ":" + location.port + "/snowplow_post", {
  appId: "searchHub",
  platform: "web",
  post: true,
  bufferSize: 1,
  contexts: {
    webPage: true,
    performanceTiming: true,
    gaCookies: true,
    geolocation: true
  }
});

searchhub_snowplow('enableActivityTracking', 30, 30);
//searchhub_snowplow('enableLinkClickTracking', {'blacklist':['no-track']}, true, true);
//searchhub_snowplow('refreshLinkClickTracking');
searchhub_snowplow('trackPageView', null, [{
          schema: "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
          data: {"signalType": "pageView"}
        }]);
