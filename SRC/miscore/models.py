from django.db import models
from decimal import Decimal
from django.db.models import Sum
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class University(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.name

class School(models.Model):
    university = models.ForeignKey(
        University, on_delete=models.PROTECT, related_name="schools",
        null=True, blank=True
    )
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name} ({self.university})" if self.university_id else self.name

class Faculty(models.Model):
    school = models.ForeignKey('School', on_delete=models.PROTECT, related_name='faculties')
    code   = models.CharField(max_length=50, unique=True)  # duy nhất toàn bảng
    name   = models.CharField(max_length=255)

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  
    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)

class Major(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name="majors")
    school  = models.ForeignKey(School,  on_delete=models.PROTECT, related_name="majors", editable=False)

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.faculty_id:
            self.school_id = self.faculty.school_id

    def save(self, *args, **kwargs):
        if self.faculty_id:
            self.school_id = self.faculty.school_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)

class Lecturer(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name="lecturers")
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="lecturers", editable=False)

    name     = models.CharField(max_length=255)
    position = models.CharField(max_length=100, blank=True)
    email    = models.EmailField(max_length=255, blank=True)
    phone    = models.CharField(max_length=25, blank=True)

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # đảm bảo luôn đồng bộ trước khi validate/save
        if self.faculty_id:
            self.school_id = self.faculty.school_id

    def save(self, *args, **kwargs):
        # phòng trường hợp clean() không được gọi
        if self.faculty_id:
            self.school_id = self.faculty.school_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


# ==== COURSES =========================================================
def _validate_half_step(value, field_label):
    """
    Chỉ cho phép bội số 0.5 (0.5, 1.0, 1.5, ...).
    """
    if value is None:
        return
    v = Decimal(value)
    # nhân 2 phải ra số nguyên
    if (v * 2) % 1 != 0:
        raise ValidationError({field_label: "Giá trị phải là bội số của 0.5 (ví dụ 0.5, 1.0, 1.5, ...)."})

class Course(models.Model):
    code = models.CharField("Mã học phần", max_length=20, unique=True)
    name = models.CharField("Tên học phần", max_length=500)

    # Số tín và 3 thành phần — mặc định LT/TH/Tự học = 0
    credits      = models.DecimalField("Số tín",     max_digits=4, decimal_places=1)
    credits_lt   = models.DecimalField("Tín LT",     max_digits=4, decimal_places=1, default=Decimal("0.0"))
    credits_th   = models.DecimalField("Tín TH",     max_digits=4, decimal_places=1, default=Decimal("0.0"))

    faculty = models.ForeignKey(
        Faculty, on_delete=models.PROTECT, related_name="courses", verbose_name="Khoa quản lý"
    )

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- Validate ở mức Model ---
    def clean(self):
        # bước 0.5 cho tất cả các trường số tín
        _validate_half_step(self.credits, "credits")
        _validate_half_step(self.credits_lt, "credits_lt")
        _validate_half_step(self.credits_th, "credits_th")

        # không âm, và tổng khớp
        for f in ("credits", "credits_lt", "credits_th"):
            v = getattr(self, f)
            if v is None:
                continue
            if v < 0:
                raise ValidationError({f: "Không được âm."})

        if self.credits is None:
            raise ValidationError({"credits": "Bắt buộc nhập số tín."})

        # số tín tối thiểu 0.5
        if self.credits < Decimal("0.5"):
            raise ValidationError({"credits": "Số tín phải ≥ 0.5."})

        # tổng = LT + TH + tự học
        if (self.credits_lt or 0) + (self.credits_th or 0) != self.credits:
            raise ValidationError("Số tín phải bằng: Tín LT + Tín TH .")

        # quy tắc “hai cái có thể bằng 0, cái còn lại = số tín” (trường hợp dùng số 0)
        if self.credits_lt == 0 and self.credits_th != self.credits:
            raise ValidationError("Khi Tín LT = 0 thì Tín TH phải bằng đúng Số tín.")
        if self.credits_th == 0 and self.credits_lt != self.credits:
            raise ValidationError("Khi Tín TH = 0 thì Tín LT phải bằng đúng Số tín.")

    def __str__(self):
        return f"{self.code} — {self.name}"

    class Meta:
        ordering = ("code",)
        constraints = [
            # tổng khớp ở mức DB
            models.CheckConstraint(
                name="course_sum_match",
                check=Q(credits=F("credits_lt") + F("credits_th") ),
            ),
            # không âm
            models.CheckConstraint(
                name="course_non_negative",
                check=Q(credits__gte=0) & Q(credits_lt__gte=0) & Q(credits_th__gte=0) ,
            ),
            # tối thiểu 0.5 cho số tín
            models.CheckConstraint(
                name="course_credit_min",
                check=Q(credits__gte=Decimal("0.5")),
            ),
        ]




class Curriculum(models.Model):
    major = models.ForeignKey("miscore.Major", on_delete=models.PROTECT, related_name="curriculums", verbose_name="Ngành")
    faculty = models.ForeignKey("miscore.Faculty", on_delete=models.PROTECT, related_name="curriculums", verbose_name="Khoa quản lý")
    year = models.PositiveIntegerField("Năm áp dụng")

    def clean(self):
        if self.major_id and self.faculty_id and self.major.faculty_id != self.faculty_id:
            raise ValidationError({"faculty": "Khoa quản lý phải trùng với Khoa của Ngành đã chọn."})

    def save(self, *args, **kwargs):
        if self.major_id:
            self.faculty = self.major.faculty
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.major} — {self.year}"

    class Meta:
        unique_together = ("major", "year")
        ordering = ("major__name", "-year")








# ----- ListCourse tách riêng -----
class ListCourse(models.Model):
    class RequirementType(models.TextChoices):
        COMPULSORY = "COMPULSORY", "Bắt buộc"
        ELECTIVE   = "ELECTIVE",   "Tự chọn"

    semester_no      = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])
    requirement_type = models.CharField(max_length=20, choices=RequirementType.choices)
    category         = models.CharField(max_length=50, blank=True, default="")
    notes            = models.TextField(blank=True, default="")
    is_active        = models.BooleanField(default=True)

    course      = models.ForeignKey("miscore.Course", on_delete=models.PROTECT, related_name="listcourse_items")
    curriculum  = models.ForeignKey("miscore.Curriculum", on_delete=models.CASCADE, related_name="listcourse_items")

    class Meta:
        db_table = "miscore_listcourse"      # bám đúng tên bảng trong DB
        unique_together = (("curriculum", "course"),)
        indexes = [
            models.Index(fields=["curriculum", "semester_no"]),
            models.Index(fields=["curriculum", "requirement_type"]),
            models.Index(fields=["curriculum", "category"]),
            models.Index(fields=["course"]),
        ]
        ordering = ("semester_no", "course__code")
        verbose_name = "học phần trong CTĐT"
        verbose_name_plural = "học phần trong CTĐT"

    def __str__(self):
        return f"{self.curriculum} — {self.course.code}"


class ListCourseRelation(models.Model):
    class RelationType(models.TextChoices):
        PREREQUISITE = "PREREQUISITE", "Tiên quyết"
        PREPARATORY  = "PREPARATORY",  "Học trước"
        COREQUISITE  = "COREQUISITE",  "Song hành"

    relation_type = models.CharField(max_length=20, choices=RelationType.choices)
    course_item   = models.ForeignKey("miscore.ListCourse", on_delete=models.CASCADE, related_name="relations_from")
    curriculum    = models.ForeignKey("miscore.Curriculum", on_delete=models.CASCADE, related_name="relations")
    related_item  = models.ForeignKey("miscore.ListCourse", on_delete=models.CASCADE, related_name="relations_to")

    class Meta:
        db_table = "miscore_listcourserelation"
        unique_together = (("curriculum", "course_item", "related_item", "relation_type"),)
        indexes = [
            models.Index(fields=["curriculum", "course_item"]),
            models.Index(fields=["curriculum", "related_item"]),
            models.Index(fields=["curriculum", "relation_type"]),
        ]
        verbose_name = "quan hệ học phần"
        verbose_name_plural = "quan hệ học phần"

    def __str__(self):
        return f"{self.course_item} -> {self.related_item} ({self.relation_type})"


# ----- Proxy dùng riêng để quản trị ListCourse (KHÔNG đụng CurriculumAdmin thật) -----
class CurriculumForManage(Curriculum):
    class Meta:
        proxy = True
        verbose_name = "Quản lý học phần CTĐT"
        verbose_name_plural = "Quản lý học phần CTĐT"




########

class Tuition(models.Model):
    """
    Học phí theo CTĐT. total_credits được tính từ ListCourse (is_active=True).
    """
    curriculum = models.OneToOneField(
        "miscore.Curriculum",
        on_delete=models.CASCADE,
        db_column="curriculum_id",
        related_name="tuition",
    )
    # Cho phép bước 0.5 nên lưu 1 chữ số thập phân
    total_credits = models.DecimalField(
        max_digits=6, decimal_places=1, default=Decimal("0.0"), verbose_name="Tổng tín"
    )
    price_per_credit = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(0)],
        verbose_name="Giá / tín"
    )
    total_amount = models.DecimalField(
        max_digits=16, decimal_places=2, default=Decimal("0.00"), verbose_name="Thành tiền"
    )
    note = models.CharField(max_length=255, blank=True, default="", verbose_name="Ghi chú")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật")

    class Meta:
        db_table = "miscore_tuition"
        verbose_name = "Học phí CTĐT"
        verbose_name_plural = "Học phí CTĐT"

    # ---- TÍNH TỔNG TÍN từ ListCourse ----
    @staticmethod
    def calc_total_credits(curriculum):
        """
        Cộng tín từ các dòng ListCourse active của curriculum.
        Linh hoạt tên trường tín chỉ của Course:
          - ưu tiên các tên: total_credits, credits, credit_total, tin_chi, so_tin_chi, so_tin
          - nếu không có, sẽ cộng lt + th (credit_lt/credit_th hoặc lt/th hoặc tin_lt/tin_th)
        """
        from .models import ListCourse  # tránh import vòng
        items = (
            ListCourse.objects
            .filter(curriculum=curriculum, is_active=True)
            .select_related("course")
        )

        total = Decimal("0.0")
        for it in items:
            c = it.course
            # lần lượt thử các tên trường "tổng tín"
            value = None
            for name in ["total_credits", "credits", "credit_total", "tin_chi", "so_tin_chi", "so_tin"]:
                if hasattr(c, name):
                    v = getattr(c, name) or 0
                    value = Decimal(str(v))
                    break
            if value is None:
                # fallback: cộng LT + TH theo các tên thường gặp
                def pick(obj, *names):
                    for n in names:
                        if hasattr(obj, n):
                            return getattr(obj, n) or 0
                    return 0
                lt = Decimal(str(pick(c, "credit_lt", "lt", "tin_lt")))
                th = Decimal(str(pick(c, "credit_th", "th", "tin_th")))
                value = lt + th

            total += value

        # làm tròn về 1 chữ số thập phân (bước 0.5/0.1)
        return total.quantize(Decimal("0.0"))

    def recalc(self):
        """Tính lại tổng tín & thành tiền từ giá hiện tại."""
        total = self.calc_total_credits(self.curriculum)
        self.total_credits = total
        self.total_amount = (self.price_per_credit or Decimal("0.00")) * total

    def save(self, *args, **kwargs):
        # mỗi lần lưu đều tự tính lại để đảm bảo đồng bộ
        self.recalc()
        super().save(*args, **kwargs)
    
    @classmethod
    def calc_total_credits(cls, curriculum):
        from .models import Course  # hoặc import trên đầu file nếu tiện
        s = (Course.objects
             .filter(listcourse_items__curriculum=curriculum,
                     listcourse_items__is_active=True)
             .aggregate(s=Sum("credits"))["s"])
        return (s or Decimal("0"))

    def recalc(self):
        tot = self.calc_total_credits(self.curriculum)
        self.total_credits = tot
        price = self.price_per_credit or Decimal("0")
        self.total_amount = (tot or Decimal("0")) * price

 
class Profile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Sinh viên"
        STAFF   = "STAFF",   "Cán bộ/Giảng viên"
        OFFICE  = "OFFICE",  "Phòng ban"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        unique=True,
        verbose_name="Tài khoản"
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name="Vai trò"
    )
    dept = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Khoa/Phòng"
    )
    idcode = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Mã định danh (MSSV/Mã CB)"
    )

    class Meta:
        db_table = "miscore_profile"
        verbose_name = "Hồ sơ tài khoản"
        verbose_name_plural = "Hồ sơ tài khoản"

    def role_label(self):
        return self.get_role_display()

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"     


# Tạo một proxy đứng riêng trên menu Admin
class CurriculumCopyTool(Curriculum):
    class Meta:
        proxy = True
        verbose_name = "Sao chép CTĐT"
        verbose_name_plural = "Sao chép CTĐT"
   