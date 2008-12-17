
from django.contrib import admin

class VideoAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_added'
    fields = (('General Information',
               {'fields': ('title', 'video', 'time', 'kind',
                           'cover_art')}),
              ('Searching Metadata',
               {'fields': ('tags', 'visible')}))
    list_display = ('title', 'time_string', 'date_added', 'visible')
    list_display_links = ('title',)
    list_filter = ('visible', 'date_added')
    search_fields = ('title',)

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'pipe', 'last_touched')
    list_display_links = ('name',)

admin.site.register(VideoAdmin)
admin.site.register(ChannelAdmin)
