from django.contrib import admin
from .models import (
     Level, Subject, PastPaper, Syllabus, Guide,
    TopicalNote, Textbook, Purchase, Payment,
    Topic, TopicResource, ZimsecInfo
)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'level']
    list_filter = ['level']
    search_fields = ['name']


@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ['paper_name', 'subject', 'session', 'year', 'is_locked']
    list_filter = ['subject', 'session', 'year', 'is_locked']
    search_fields = ['paper_name', 'subject__name']
    ordering = ['-year']


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ['subject', 'effective_from', 'effective_to', 'is_active']
    list_filter = ['is_active', 'subject__level']
    search_fields = ['subject__name']

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'uploaded_by', 'uploaded_at', 'is_approved']
    list_filter = ['is_approved', 'subject__level', 'uploaded_at']
    search_fields = ['title', 'subject__name']
    actions = ['approve_guides']
    
    def approve_guides(self, request, queryset):
        queryset.update(is_approved=True)
    approve_guides.short_description = "Approve selected guides"


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject']
    list_filter = ['subject__level']
    search_fields = ['name']


@admin.register(TopicalNote)
class TopicalNoteAdmin(admin.ModelAdmin):
    list_display = ['subject',  'uploaded_at', 'is_approved']
    list_filter = ['subject__level', 'is_approved']
    search_fields = ['topic', 'subject__name']

@admin.register(Textbook)
class TextbookAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'author', 'price', 'is_published']
    list_filter = ['subject__level', 'is_published']
    search_fields = ['title', 'author', 'subject__name']

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'textbook', 'amount_paid', 'purchased_at']
    list_filter = ['purchased_at']
    search_fields = ['user__username', 'textbook__title']

@admin.register(ZimsecInfo)
class ZimsecInfoAdmin(admin.ModelAdmin):
    list_display = ['title', 'last_updated']
    search_fields = ['title']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'textbook', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'textbook__title', 'paynow_reference']
    readonly_fields = ['paynow_reference', 'poll_url', 'created_at', 'updated_at']