FROM grahamdumpleton/mod-wsgi-docker:python-2.7-onbuild
USER $MOD_WSGI_USER:$MOD_WSGI_GROUP
CMD [ "searchhub.wsgi", "--url-alias", "/assets", "./server/assets", "--compress-responses"]

