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

from django.shortcuts import render_to_response
from django.template import RequestContext
import operator
from models import apks
from django.db.models import Q


def main(request):
    return aresponse(request)

def app(request,id):
    return aresponse(request,id)


def search_keywords(apks, keywords):
    if isinstance(keywords, str):
        keywords = [keywords]

    if not isinstance(keywords, list):
        return None

    nameSearch = [Q(nombre__icontains=x) for x in keywords]
    pathSearch = [Q(ruta__icontains=x) for x in keywords]

    final_q = reduce(operator.or_, nameSearch + pathSearch)
    r_qs = apks.objects.filter(final_q)
    return r_qs


def aresponse(request,id=None):
    c = RequestContext(request)

    from forms import SearchForm
    sform = SearchForm()

    if request.method == 'GET' and not id:
        return render_to_response("main.html",{"err":False,"sform":sform},context_instance=c)
    elif request.method == 'GET':
        apk = apks.objects.get(ind=id)

        rel = apk.relativo.split(":")
        if len(rel)>0:
            del rel[0]
        import os
        dir = os.path.dirname(apk.ruta)

        return render_to_response("desc.html",{"dir":dir,"rel":rel,"apk":apk,"err":False,"sform":sform},context_instance=c)
    elif request.method == 'POST':
        asearch = request.POST['asearch']
        searchp = asearch.split()
        if len(searchp) == 0:
            return render_to_response("main.html",{"err":False,"sform":sform},context_instance=c)

        apk = search_keywords(apks,searchp)

        if len(apk) > 0:
            return render_to_response("main.html",{"err":False,"cursor":apk,"sform":sform},context_instance=c)
        else:
            return render_to_response("main.html",{"msg":"No se han encontrado coincidencias","err":True,"sform":sform},context_instance=c)
