from django.contrib import admin
from mailer.models import Message, DontSendEntry, MessageLog, Attachment


class AttachmentInlineAdmin(admin.TabularInline):
    model = Attachment
    extra = 0


class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "to_address", "subject", "when_added", "priority")
    inlines = (AttachmentInlineAdmin,)


class DontSendEntryAdmin(admin.ModelAdmin):
    list_display = ("to_address", "when_added")


class MessageLogAdmin(admin.ModelAdmin):
    list_display = ("id", "to_address", "subject", "when_attempted", "result")
    search_fields = ("to_address",)


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("message", "attachment_file")
    raw_id_fields = ("message",)


admin.site.register(Message, MessageAdmin)
admin.site.register(DontSendEntry, DontSendEntryAdmin)
admin.site.register(MessageLog, MessageLogAdmin)
admin.site.register(Attachment, AttachmentAdmin)
