#!/bin/sh
# This "script" is intended to sync to a webserver folder using rsync.
# Change it to convenience. 
# It's intented to run both from the photobooth software or manually
# It expects proper ssh-keys to be deployed on the server.
#
# Example layout:
#   - server hostname: my.server.com 
#   - ssh username: someuser
#   - photobooth web root: /path/to/www/photos
#   - photobooth web url: https://photos.server.com/
# 	- the photo "abc.jpg" will be accesible on the URL 
#	  https://photos.server.com/abc.jpg

rsync -avz . someuser@my.server.com:/path/to/www/photos