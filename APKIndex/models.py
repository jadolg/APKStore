#  models.py
# -*- coding: UTF-8 -*-

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

from django.db import models

class apks(models.Model):
    sha = models.TextField(max_length=64, primary_key=True)
    nombre = models.CharField(max_length=30)
    icon = models.TextField()
    descripcion = models.TextField()
    ruta = models.TextField()
    versionName = models.CharField(max_length=20)
    version = models.TextField()
    pool = models.TextField()
    ind = models.IntegerField()
    relativo = models.TextField()

    def __str__(self):
        return self.nombre+" "+self.version
