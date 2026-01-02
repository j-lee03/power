from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, EventDocument



class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = '조직 및 직급 설정'
    verbose_name = '사원 정보'



class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    list_display = ('username', 'get_group_info', 'get_role_korean', 'is_staff')

    def get_role_korean(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else '-'
    get_role_korean.short_description = '직급'


    def get_group_info(self, obj):
        if not hasattr(obj, 'profile'):
            return '-'

        dept = obj.profile.get_department_display()
        team = obj.profile.get_team_display()

        if obj.profile.team == 'NONE':
            return dept
        return f"{dept} / {team}"
    get_group_info.short_description = '소속 (대분류/중분류)'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)



@admin.register(EventDocument)
class EventDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_read_role', 'get_write_role', 'uploaded_at')
    list_filter = ('read_level', 'write_level')
    search_fields = ('title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        my_role = getattr(request.user, 'profile', None) and request.user.profile.role or 0
        return qs.filter(read_level__lte=my_role)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or obj is None: return True
        my_role = getattr(request.user, 'profile', None) and request.user.profile.role or 0
        return my_role >= obj.write_level

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or obj is None: return True
        my_role = getattr(request.user, 'profile', None) and request.user.profile.role or 0
        return my_role >= obj.write_level

    def get_read_role(self, obj): return obj.get_read_level_display()
    get_read_role.short_description = '열람 가능'
    def get_write_role(self, obj): return obj.get_write_level_display()
    get_write_role.short_description = '수정 가능'