from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'APKIndex.views.main', name='main'),
    url(r'^(\d+)$', 'APKIndex.views.app', name='app'),
    # url(r'^APKStore/', include('APKStore.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
