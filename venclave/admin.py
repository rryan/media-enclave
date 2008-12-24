
from django.contrib import admin

from menclave.venclave.models import ContentNode, Channel

class ContentNodeAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
#     fields = (('General Information',
#                {'fields': ('title', 'path', 'content', 'kind',
#                            'cover_art')}),
#               ('Searching Metadata',
#                {'fields': ('tags', 'visible')}))
    list_display = ('title', 'created', 'visible')
    list_display_links = ('title',)
    list_filter = ('visible', 'created')
    search_fields = ('title',)

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'pipe', 'last_touched')
    list_display_links = ('name',)

admin.site.register(ContentNode, ContentNodeAdmin) 
admin.site.register(Channel, ChannelAdmin)
