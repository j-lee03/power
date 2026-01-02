from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError




import os


ROLE_CHOICES = (
    (0, '스텝 (Staff)'),
    (1, '파트장 (Part Leader)'),
    (2, '팀장 (Team Leader)'),
    (3, '전체 (Admin)'),
)

DEPT_CHOICES = (
    ('FACILITY', '시설팀'),
    ('OFFICE', '사무팀'),
    ('COOP', '업무협업팀'),
)

TEAM_CHOICES = (
    ('NONE', '- (없음)'),
    ('SOUND', '무대음향'),
    ('LIGHT', '무대조명'),
    ('VIDEO', '무대영상'),
    ('GUIDE', '무대계도'),
    ('ACCOUNT', '회계팀'),
    ('HR', '인재관리팀'),
)


VALID_TEAMS = {
    'FACILITY': ['SOUND', 'LIGHT', 'VIDEO', 'GUIDE'],
    'OFFICE':   ['ACCOUNT', 'HR'],
    'COOP':     ['NONE'],
}

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.IntegerField(choices=ROLE_CHOICES, default=0, verbose_name="직급")
    department = models.CharField(max_length=20, choices=DEPT_CHOICES, default='COOP', verbose_name="대분류")
    team = models.CharField(max_length=20, choices=TEAM_CHOICES, default='NONE', verbose_name="중분류")

    def __str__(self):
        dept = self.get_department_display()
        team = self.get_team_display()
        role = self.get_role_display()
        if self.team == 'NONE':
            return f"{self.user.username} [{dept} - {role}]"
        return f"{self.user.username} [{dept}/{team} - {role}]"

    def clean(self):
        allowed_teams = VALID_TEAMS.get(self.department, [])
        if self.team not in allowed_teams:
            raise ValidationError(f"'{self.get_department_display()}'에는 해당 팀을 지정할 수 없습니다.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class EventDocument(models.Model):
    title = models.CharField(max_length=200, blank=True, verbose_name="문서 제목")
    content = models.TextField(blank=True, verbose_name="내용 요약")
    pdf_file = models.FileField(upload_to='pdfs/%Y/%m/', null=True, blank=True, verbose_name="첨부 파일")
    read_level = models.IntegerField(choices=ROLE_CHOICES, default=0, verbose_name="공개 범위")
    write_level = models.IntegerField(choices=ROLE_CHOICES, default=1, verbose_name="수정 권한")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or '(제목 없음)'

    def save(self, *args, **kwargs):
        if self.pdf_file and not self.title:
            self.title = os.path.basename(self.pdf_file.name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.pdf_file:
            self.pdf_file.delete()
        super().delete(*args, **kwargs)

class Document(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    file_data = models.BinaryField(null=True, blank=True)
    filename = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title