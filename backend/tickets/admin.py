from django.contrib import admin
from .models import Ticket, TicketComment, TicketHistory


class TicketCommentInline(admin.TabularInline):
    """Inline display of comments in ticket admin"""
    model = TicketComment
    extra = 0
    fields = ('author', 'comment', 'is_staff_comment', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


class TicketHistoryInline(admin.TabularInline):
    """Inline display of history in ticket admin"""
    model = TicketHistory
    extra = 0
    fields = ('changed_by', 'field_changed', 'old_value', 'new_value', 'change_reason', 'created_at')
    readonly_fields = ('changed_by', 'field_changed', 'old_value', 'new_value', 'change_reason', 'created_at')
    can_delete = False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin interface for Ticket model"""
    
    list_display = (
        'ticket_number',
        'subject',
        'customer',
        'category',
        'priority',
        'status',
        'created_at',
        'updated_at'
    )
    
    list_filter = (
        'status',
        'priority',
        'category',
        'created_at',
        'updated_at'
    )
    
    search_fields = (
        'ticket_number',
        'subject',
        'description',
        'customer__username',
        'customer__business_name',
        'customer__email'
    )
    
    readonly_fields = (
        'ticket_number',
        'created_at',
        'updated_at',
        'resolved_at',
        'closed_at'
    )
    
    fieldsets = (
        ('Ticket Information', {
            'fields': (
                'ticket_number',
                'customer',
                'order',
                'subject',
                'description'
            )
        }),
        ('Classification', {
            'fields': (
                'category',
                'priority',
                'status'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'resolved_at',
                'closed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TicketCommentInline, TicketHistoryInline]
    
    date_hierarchy = 'created_at'
    
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related('customer', 'order')


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    """Admin interface for TicketComment model"""
    
    list_display = (
        'ticket',
        'author',
        'is_staff_comment',
        'created_at',
        'comment_preview'
    )
    
    list_filter = (
        'is_staff_comment',
        'created_at'
    )
    
    search_fields = (
        'ticket__ticket_number',
        'author__username',
        'comment'
    )
    
    readonly_fields = ('created_at',)
    
    date_hierarchy = 'created_at'
    
    ordering = ('-created_at',)
    
    def comment_preview(self, obj):
        """Show first 50 characters of comment"""
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment Preview'


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    """Admin interface for TicketHistory model"""
    
    list_display = (
        'ticket',
        'field_changed',
        'old_value',
        'new_value',
        'changed_by',
        'created_at'
    )
    
    list_filter = (
        'field_changed',
        'created_at'
    )
    
    search_fields = (
        'ticket__ticket_number',
        'changed_by__username',
        'field_changed',
        'change_reason'
    )
    
    readonly_fields = (
        'ticket',
        'changed_by',
        'field_changed',
        'old_value',
        'new_value',
        'change_reason',
        'created_at'
    )
    
    date_hierarchy = 'created_at'
    
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        """Prevent manual creation of history entries"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of history entries"""
        return False

