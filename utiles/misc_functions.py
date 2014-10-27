#-*-coding:utf-8-*-

#  views.py
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


from django.db.models import Q
import random
from fillDB import get_data, extract_icon
import operator
import os
from shutil import copy
from hashlib import sha256

from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'APKStore.settings')

from APKIndex.models import apks

def search_keywords(apks, keywords):
    if isinstance(keywords, str):
        keywords = [keywords]

    if not isinstance(keywords, list):
        return None

    nameSearch = [Q(nombre__icontains=x) for x in keywords]
    pathSearch = [Q(ruta__icontains=x) for x in keywords]

    ns = []
    ps = []
    ns.append(reduce(operator.or_,nameSearch))
    ps.append(reduce(operator.or_,pathSearch))

    final_q = reduce(operator.and_, ns + ps)
    print final_q
    r_qs = apks.objects.filter(final_q).order_by("nombre")
    return r_qs

def handle_uploaded_file(afile):
    path = '/tmp/'+afile.name
    with open(path, 'wb+') as destination:
        for chunk in afile.chunks():
            destination.write(chunk)
    data = get_data(path)

    if data != None:
        ind = data[3]
        nombre = data[0][:30]

        icon = extract_icon(path,ind)

        versionName = data[2][:20]
        version = data[3]

        d = open(path,"rb").read(512)
        thash = sha256(d)
        sha =  thash.hexdigest()

        aux = apks.objects.filter(sha=sha)

        if len(aux) > 0:
            raise Exception('aplicacion duplicada')

        a = apks(sha=sha,nombre=nombre,icon=icon,descripcion="",ruta=data[0]+"_"+str(ind)+"/"+afile.name,versionName=versionName,version=version,pool=999,ind=ind,relativo="")
        a.save()

        os.mkdir(settings.UPLOAD_POOL+"/"+data[0]+"_"+str(ind))
        copy(path,settings.UPLOAD_POOL+"/"+data[0]+"_"+str(ind))
        os.remove(path)
    else:
        raise Exception('no se obtuvieron datos')






