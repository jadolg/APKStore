#  urls.py
# -*- coding: UTF-8 -*-
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

from django.conf.urls import patterns, url, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler404 = 'APKIndex.views.a404_view'
handler500 = 'APKIndex.views.a500_view'

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'APKIndex.views.main', name='main'),
    url(r'^all$', 'APKIndex.views.all', name='all'),
    url(r'^buscar/(.*?)/(\d+)$', 'APKIndex.views.search', name='search'),
    url(r'^adicionales/(\d+)$', 'APKIndex.views.app', name='app'),
    url(r'^upload/$', 'APKIndex.views.upload', name='upload'),

    url(r'^success/upload/$', 'APKIndex.views.SuccUpload', name='SuccUpload'),
    url(r'^error/upload/$', 'APKIndex.views.ErrUpload', name='ErrUpload'),


    # url(r'^APKStore/', include('APKStore.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
