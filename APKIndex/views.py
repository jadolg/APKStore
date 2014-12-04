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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http.response import HttpResponseRedirect

from django.shortcuts import render_to_response
from django.template import RequestContext

from forms import UploadFileForm
from utiles.misc_functions import handle_uploaded_file

from models import apks
from utiles.misc_functions import search_keywords

def defbuscar(f):
    def checkSearch(request):
        if request.GET.has_key('asearch'):
            keywords= request.GET['asearch']

            if keywords == "":
                keywords = "*all*"

            page = 1
            if request.GET.has_key('page'):
                page = request.GET['page']
            return HttpResponseRedirect('/buscar/'+keywords+'/'+str(page))
        else:
            return False

    def wrapper(*arg):
        s = checkSearch(arg[0])
        if  s != False:
            return s
        else:
            return f(*arg)
    return wrapper

@defbuscar
def main(request):
    return aresponse(request)

@defbuscar
def app(request,id):
    return aresponse(request,id)

@defbuscar
def all(request):
    return search(request,keywords="*all*")

@defbuscar
def search(request,keywords,page=1):
    return aresponse(request,keywords=keywords,page=page)

@defbuscar
def upload(request):
    c = RequestContext(request)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            code = handle_uploaded_file(request.FILES['file'])
            if code == 0 :
                return HttpResponseRedirect('/success/upload/')
            elif code == 1:
                return HttpResponseRedirect('/error/duplicated/')
            elif code == 2:
                return HttpResponseRedirect('/error/upload/')
        else:
            return HttpResponseRedirect('/error/upload/')

    else:
        form = UploadFileForm()

    return render_to_response('upload.html', {'err':False,'form': form},context_instance=c)

@defbuscar
def SuccUpload(request):
    return aresponse(request,msg="Aplicación almacenada satisfactoriamente")

@defbuscar
def ErrUpload(request):
    return aresponse(request,msg="Ocurrió un error mientras se subía o procesaba la aplicación")

@defbuscar
def DupUpload(request):
    return aresponse(request,msg="Ya tenemos esta aplicación. Gracias por compartir ;)")

def aresponse(request,id=None,keywords=None,page=None,msg=None):
    c = RequestContext(request)

    from forms import SearchForm
    sform = SearchForm()

    if request.method == 'GET':
        if id:
            apk = apks.objects.get(ind=id)

            rel = apk.relativo.split(":")
            if len(rel)>0:
                del rel[0]
            import os
            dir = os.path.dirname(apk.ruta)

            return render_to_response("desc.html",{"dir":dir,"rel":rel,"apk":apk,"err":False,"sform":sform},context_instance=c)
        elif keywords != None and page != None:
            asearch = keywords
            searchp = asearch.split()
            
            if len(searchp) == 0:
                return render_to_response("main.html",{"err":False,"sform":sform},context_instance=c)

            if keywords == "*all*":
                apk = apks.objects.order_by("nombre")
            else:
                apk = search_keywords(apks,searchp)

            paginator = Paginator(apk,20)
            try:
                lapk = paginator.page(page)
            except PageNotAnInteger:
                lapk = paginator.page(1)
            except EmptyPage:
                lapk = paginator.page(paginator.num_pages)


            if len(apk) > 0:
                return render_to_response("main.html",{"err":False,"cursor":lapk,"asearch":asearch,"sform":sform},context_instance=c)
            else:
                return render_to_response("main.html",{"err":True,"msg":"No se han encontrado coincidencias","sform":sform},context_instance=c)

        elif msg != None:
            return render_to_response("main.html",{"err":True,"msg":msg,"sform":sform},context_instance=c)
        else:
            return render_to_response("index.html",{"err":False,"cursor":[],"sform":sform},context_instance=c)
    else:
        pass

@defbuscar
def a404_view(request):
    return aresponse(request,msg="La página solicitada no existe.")

@defbuscar
def a500_view(request):
    return aresponse(request,msg="Oooops. Ha ocurrido un error :(")