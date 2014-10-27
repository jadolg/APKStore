#!/usr/bin/env python
# -*- coding: UTF-8 -*

#  cherryd.py
#
#  Copyright 2014 Jorge Alberto Díaz Orozco <jaorozco@estudiantes.uci.cu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.


import os
import socket
import urllib
import urlparse
import cherrypy
from APKStore import settings
from pydaemonlib.pydaemonlib import Daemon
from sys import argv
from sys import exit as Exit
from pyQR.pyQR import *

# Django settings
#~ sys.path.append(os.path.abspath(os.getcwd())+'/WebBlog')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'APKStore.settings')
# Celery loader
os.environ['CELERY_LOADER'] = 'djcelery.loaders.DjangoLoader'


class DjangoApplication(object):
    def __init__(self):
        self.servers = []
        self.domains = {}
 
    def add_server(self, netloc, path, config):
        """Add a new CherryPy Application for a Virtual Host.
 
        Creates a new CherryPy WSGI Server instance if the host resolves
        to a different IP address or port.
 
        """
        from cherrypy._cpwsgi_server import CPWSGIServer
        from cherrypy.process.servers import ServerAdapter
 
        host, port = urllib.splitnport(netloc, 80)
        host = socket.gethostbyname(host)
        bind_addr = (host, port)
        if bind_addr not in self.servers:
            self.servers.append(bind_addr)
            server = CPWSGIServer()
            server.bind_addr = bind_addr
            adapter = ServerAdapter(cherrypy.engine, server, server.bind_addr)
            adapter.subscribe()
        self.domains[netloc] = cherrypy.Application(root=None,
            config={path.rstrip('/') or '/': config})
 
    def cfg_assets(self, url, root):
        """Configure hosting of static and media asset directories.
 
        Can either mount to a specific path or add a Virtual Host. Sets
        Expires header to 1 year.
 
        """
        url_parts = urlparse.urlsplit(url)
        path = url_parts.path.rstrip('/')
        config = {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': root,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 24 * 365, # 1 year
            'tools.gzip.on': True,
            'tools.gzip.mime_types': [
                'text/*',
                'application/javascript',
                'application/x-javascript',
            ],
        }
        if url_parts.netloc:
            self.add_server(url_parts.netloc, path, config)
        elif path:
            cherrypy.tree.mount(None, path, {'/': config})
 
    def cfg_favicon(self, root):
        """Configure a default favicon.
 
        Expects it to be in STATIC_ROOT.
 
        """
        favicon = os.path.join(root, 'favicon.png')
        config = {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': favicon,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 24 * 365, # 1 year
        }
        cherrypy.tree.mount(None, '/favicon.png', {'/': config})
 
    def run(self, host='localhost',port=8000, reload=True, log=True):
        """Run the CherryPy server."""
        from django.conf import settings
        from django.core.handlers.wsgi import WSGIHandler

        cherrypy.config.update({
            'server.socket_host': host,
            'server.socket_port': port,
            'log.screen': log,
            'engine.autoreload_on': reload,
        })
        self.cfg_assets(settings.MEDIA_URL, settings.MEDIA_ROOT)
        self.cfg_assets(settings.STATIC_URL, settings.STATIC_ROOT)
        c = 0
        for i in settings.APK_ROOT:
            self.cfg_assets("/apk"+str(c)+"/",i)
            c += 1

        self.cfg_assets("/apk999/",settings.UPLOAD_POOL)

        self.cfg_assets(settings.ICONS_URL,settings.ICONS_ROOT)
        self.cfg_favicon(settings.STATIC_ROOT)
        app = WSGIHandler()
        if self.domains:
            app = cherrypy.wsgi.VirtualHost(app, self.domains)

        cherrypy.tree.graft(app)
        cherrypy.engine.start()
        cherrypy.engine.block()


def main(**kwargs):
    app = DjangoApplication()
    app.run(**kwargs)

class server(Daemon):
    def run(self):
        main(host='0.0.0.0',port=int(settings.PORT))

 
if __name__ == '__main__':
    daemon = server('/tmp/apkstore.pid',)
    if len(argv) == 2:
        if argv[1] == 'start':
            daemon.start()
        elif argv[1] == 'stop':
            daemon.stop()
        elif argv[1] == 'restart':
            daemon.restart()
        else:
            Exit('Use: apkstore start|stop|restart')
    else:
        main(host='0.0.0.0',port=int(settings.PORT))
        #Exit('Invalid params number\nUse: apkstore start|stop|restart')
