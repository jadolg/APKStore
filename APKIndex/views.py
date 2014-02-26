# Create your views here.
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


import sqlite3
from os.path import exists

from django.shortcuts import render_to_response
from django.template import RequestContext

from APKStore.settings import DB_URL


def main(request):
    return aresponse(request)

def app(request,id):
    return aresponse(request,id)

def aresponse(request,id=None):
    c = RequestContext(request)
    DB = DB_URL

    if not exists(DB):
        raise Exception('no se encuentra la BD '+DB)

    from forms import SearchForm
    sform = SearchForm()

    if request.method == 'GET' and not id:
        return render_to_response("main.html",{"err":False,"sform":sform},context_instance=c)
    elif request.method == 'GET':
        database = sqlite3.connect(DB)
        cursor  = database.cursor()
        cursor.execute("select * from apks where id="+id)
        apk = cursor.next();
        rel = apk[7].split(":")
        if len(rel)>0:
            del rel[0]
        import os
        dir = os.path.dirname(apk[2])
        print apk
        return render_to_response("desc.html",{"dir":dir,"rel":rel,"apk":apk,"err":False,"sform":sform},context_instance=c)
    elif request.method == 'POST':
        asearch = request.POST['asearch']
        searchp = asearch.split()
        if len(searchp) == 0:
            return render_to_response("main.html",{"err":False,"sform":sform},context_instance=c)

        database = sqlite3.connect(DB)
        cursor  = database.cursor()

        q = "select * from apks where "
        for i in searchp:
            if i != searchp[-1]:
                q += "nombre like '%"+i+"%' or ruta like'%"+i+"%' and "
            else:
                q += "nombre like '%"+i+"%' or ruta like'%"+i+"%' order by nombre, version"

        cursor.execute(q)
        copy = []
        for i in cursor:
            copy.append(i)

        if len(copy) > 0:
            return render_to_response("main.html",{"err":False,"cursor":copy,"sform":sform},context_instance=c)
        else:
            return render_to_response("main.html",{"msg":"No se han encontrado coincidencias","err":True,"sform":sform},context_instance=c)
