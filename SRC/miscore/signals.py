# miscore/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ListCourse, Tuition, Profile

@receiver([post_save, post_delete], sender=ListCourse)
def _recalc_tuition_when_listcourse_changes(sender, instance, **kwargs):
    """
    Mỗi khi thêm/sửa/xóa một dòng ListCourse, cập nhật Học phí tương ứng (nếu có).
    Không bắt buộc phải tồn tại trước: nếu chưa có Tuition thì bỏ qua (tránh tự tạo ngoài ý muốn).
    """
    try:
        t = Tuition.objects.get(curriculum=instance.curriculum)
    except Tuition.DoesNotExist:
        return
    t.recalc()
    # save với skip? -> đã recalc() rồi nên cứ save bình thường
    t.save()



@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    """
    Đảm bảo mỗi User luôn có 1 Profile:
    - User mới tạo => tạo Profile (role mặc định: STUDENT).
    - User cũ được save lại => nếu Profile bị thiếu thì tạo bổ sung.
    """
    Profile.objects.get_or_create(user=instance)

