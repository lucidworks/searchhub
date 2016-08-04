FROM grahamdumpleton/mod-wsgi-docker:python-2.7-onbuild
#USER $MOD_WSGI_USER:$MOD_WSGI_GROUP
#RUN chown -R $MOD_WSGI_USER:$MOD_WSGI_GROUP /app
CMD [ "searchhub.wsgi", "--url-alias", "/assets", "./server/assets", "--compress-responses"]

