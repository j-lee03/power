from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 권한 정의
ROLE_CHOICES = (
    (0, 'GUEST'), (1, 'STAFF'), (2, 'MANAGER'), (3, 'ADMIN')
)

# [1] 사용자 확장 (직급 추가)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.IntegerField(choices=ROLE_CHOICES, default=0)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

# User 생성 시 자동으로 Profile 생성해주는 코드
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# [2] 문서 관리 (PDF) - ★ 이 부분이 없어서 에러가 난 것입니다 ★
class EventDocument(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    # PDF 업로드 (media/pdfs/연/월 폴더에 저장)
    pdf_file = models.FileField(upload_to='pdfs/%Y/%m/', null=True, blank=True)

    # 권한 설정
    read_level = models.IntegerField(choices=ROLE_CHOICES, default=1)
    write_level = models.IntegerField(choices=ROLE_CHOICES, default=2)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # 문서 삭제 시 실제 파일도 삭제하는 로직
    def delete(self, *args, **kwargs):
        if self.pdf_file:
            self.pdf_file.delete()
        super().delete(*args, **kwargs)