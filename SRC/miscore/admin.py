# miscore/admin.py

from decimal import Decimal
from io import BytesIO
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.db.models import F, OuterRef, Subquery, CharField, Sum
from django.db.models.functions import Cast, Coalesce
from django.contrib.postgres.aggregates import StringAgg
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import path, reverse

from .models import (
    University, School, Faculty, Major, Lecturer,
    Course, Curriculum, ListCourse, ListCourseRelation,
    CurriculumForManage, Tuition, Profile ,
    CurriculumCopyTool
)

# ==== REPORTLAB (PDF) ====
from .pdf_utils import render_curriculum_pdf


# ================== University ==================
@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


# ================== School ==================
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    fields = ("university", "name", "is_active")
    list_display = ("name", "university", "is_active")
    list_filter = ("university", "is_active")
    search_fields = ("name",)
    autocomplete_fields = ("university",)


# ================== Faculty ==================
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    fields = ("school", "code", "name", "is_active")
    list_display = ("code", "name", "school", "is_active")
    list_filter = ("school__university", "school", "is_active")
    search_fields = ("code", "name")
    autocomplete_fields = ("school",)


# ================== Major ==================
class MajorAdminForm(forms.ModelForm):
    school_name = forms.CharField(
        label="School",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={"style": "width: 35ch;"})
    )

    class Meta:
        model = Major
        fields = ("faculty", "school_name", "code", "name", "is_active")

    def clean(self):
        cleaned = super().clean()
        fac = cleaned.get("faculty")
        if fac:
            self.instance.school = fac.school
        return cleaned


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    form = MajorAdminForm
    fields = ("faculty", "school_name", "code", "name", "is_active")

    list_display = ("code", "name", "faculty", "school", "is_active")
    search_fields = ("code", "name")
    list_filter = ("faculty__school", "faculty", "is_active")
    autocomplete_fields = ("faculty",)

    def get_urls(self):
        urls = super().get_urls()
        my = [
            path(
                "ajax/faculty-school/",
                self.admin_site.admin_view(self.ajax_faculty_school),
                name="miscore_major_faculty_school",
            ),
        ]
        return my + urls

    def ajax_faculty_school(self, request):
        fid = request.GET.get("faculty")
        if not fid:
            return HttpResponse('{"ok": true, "school_id": null, "school_name": ""}', content_type="application/json")
        try:
            fac = Faculty.objects.select_related("school").get(pk=fid)
            return HttpResponse(
                f'{{"ok": true, "school_id": {fac.school_id if fac.school_id else "null"}, "school_name": "{str(fac.school) if fac.school_id else ""}"}}',
                content_type="application/json"
            )
        except Faculty.DoesNotExist:
            return HttpResponse('{"ok": false, "school_id": null, "school_name": ""}', content_type="application/json")

    class Media:
        js = ("miscore/autoschool.js",)


# ================== Lecturer ==================
class LecturerAdminForm(forms.ModelForm):
    school_name = forms.CharField(
        label="School",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={"style": "width: 35ch;"})
    )

    class Meta:
        model = Lecturer
        fields = ("faculty", "school_name", "name", "position", "email", "phone", "is_active")

    def clean(self):
        cleaned = super().clean()
        fac = cleaned.get("faculty")
        if fac:
            self.instance.school = fac.school
        return cleaned


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    form = LecturerAdminForm
    fields = ("faculty", "school_name", "name", "position", ("email", "phone"), "is_active")

    list_display = ("name", "faculty", "school", "position", "email", "phone", "is_active")
    search_fields = ("name", "email", "phone")
    list_filter = ("faculty__school", "faculty", "is_active")
    autocomplete_fields = ("faculty",)

    def get_urls(self):
        urls = super().get_urls()
        my = [
            path(
                "ajax/faculty-school/",
                self.admin_site.admin_view(self.ajax_faculty_school),
                name="miscore_lecturer_faculty_school",
            ),
        ]
        return my + urls

    def ajax_faculty_school(self, request):
        fid = request.GET.get("faculty")
        if not fid:
            return HttpResponse('{"ok": true, "school_id": null, "school_name": ""}', content_type="application/json")
        try:
            fac = Faculty.objects.select_related("school").get(pk=fid)
            school_name = str(fac.school) if fac.school_id else ""
            school_id = fac.school_id if fac.school_id else "null"
            return HttpResponse(f'{{"ok": true, "school_id": {school_id}, "school_name": "{school_name}"}}',
                                content_type="application/json")
        except Faculty.DoesNotExist:
            return HttpResponse('{"ok": false, "school_id": null, "school_name": ""}', content_type="application/json")

    class Media:
        js = ("miscore/autoschool.js",)


# ================== Course ==================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "faculty", "credits", "credits_lt", "credits_th", "is_active")
    list_filter = ("faculty__school", "faculty", "is_active")
    search_fields = ("code", "name")
    autocomplete_fields = ("faculty",)

    fieldsets = (
        (None, {"fields": ("code", "name", "faculty", "is_active")}),
        ("Tín chỉ", {
            "fields": (("credits", "credits_lt", "credits_th"),),
            "description": "Quy ước: bước 0.5 (0.5, 1.0, 1.5, ...). Tổng phải bằng: LT + TH."
        }),
    )


# ================== Curriculum (real) ==================
class CurriculumForm(forms.ModelForm):
    faculty_name = forms.CharField(
        label="Khoa quản lý", required=False, disabled=True,
        widget=forms.TextInput(attrs={"style": "width: 35ch;"})
    )

    class Meta:
        model = Curriculum
        fields = ("major", "faculty_name", "year")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.faculty_id:
            self.fields["faculty_name"].initial = str(self.instance.faculty)

    def clean(self):
        cleaned = super().clean()
        maj = cleaned.get("major")
        if maj and getattr(maj, "faculty_id", None):
            self.instance.faculty = maj.faculty
            self.cleaned_data["faculty_name"] = str(maj.faculty)
        else:
            self.add_error("major", "Ngành này chưa được gán Khoa quản lý.")
        return cleaned


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    form = CurriculumForm
    list_display = ("major", "faculty", "years_display")
    list_filter = ("faculty", "year")
    search_fields = ("major__code", "major__name")
    ordering = ("major__name",)
    fields = ("major", "faculty_name", "year")
    autocomplete_fields = ("major",)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("major", "faculty")

        years_sub = (
            Curriculum.objects
            .filter(major=OuterRef("major"))
            .values("major")
            .annotate(
                s=StringAgg(
                    Cast("year", output_field=CharField()),
                    delimiter=" ",
                    ordering=(F("year").desc(),)
                )
            )
            .values("s")[:1]
        )

        first_id_sub = Subquery(
            Curriculum.objects
            .filter(major=OuterRef("major"))
            .order_by("id")
            .values("id")[:1]
        )

        return (
            qs.annotate(years_str=Subquery(years_sub), first_id=first_id_sub)
              .filter(id=F("first_id"))
              .order_by("major__name")
        )

    def years_display(self, obj):
        s = getattr(obj, "years_str", "") or ""
        if not s:
            return ""
        seen, out = set(), []
        for y in s.split():
            if y not in seen:
                seen.add(y)
                out.append(y)
        return " ".join(out)
    years_display.short_description = "Năm"

    def get_urls(self):
        urls = super().get_urls()
        my = [
            path(
                "ajax/major-faculty/",
                self.admin_site.admin_view(self.ajax_major_faculty),
                name="miscore_curriculum_major_faculty",
            ),
        ]
        return my + urls

    def ajax_major_faculty(self, request):
        mid = request.GET.get("major")
        if not mid:
            return HttpResponse('{"ok": true, "faculty_id": null, "faculty_name": ""}', content_type="application/json")
        try:
            m = Major.objects.select_related("faculty").get(pk=mid)
            return HttpResponse(
                f'{{"ok": true, "faculty_id": {m.faculty_id if m.faculty_id else "null"}, "faculty_name": "{str(m.faculty) if m.faculty_id else ""}"}}',
                content_type="application/json",
            )
        except Major.DoesNotExist:
            return HttpResponse('{"ok": false, "faculty_id": null, "faculty_name": ""}', content_type="application/json")

    class Media:
        js = ("miscore/autofaculty.js",)


# ================== CurriculumForManage (proxy + 3 tầng + PDF) ==================
@admin.register(CurriculumForManage)
class CurriculumForManageAdmin(admin.ModelAdmin):
    list_display = ("major", "faculty", "year")
    list_filter = ("faculty", "year")
    search_fields = ("major__name", "major__code")
    autocomplete_fields = ("major",)

    # Cho hiện “Thêm vào” & “Thay đổi” nhưng đều điều hướng vào trang gộp /all/
    def has_add_permission(self, request): return True
    def has_change_permission(self, request, obj=None): return True

    def add_view(self, request, form_url='', extra_context=None):
        return redirect('admin:miscore_curriculumformanage_all')

    def changelist_view(self, request, extra_context=None):
        return redirect('admin:miscore_curriculumformanage_all')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        url = f"{reverse('admin:miscore_curriculumformanage_all')}?curriculum={object_id}"
        return redirect(url)

    def get_urls(self):
        urls = super().get_urls()
        my = [
            path("all/", self.admin_site.admin_view(self.manage_all),
                 name="miscore_curriculumformanage_all"),
            path("export-pdf/", self.admin_site.admin_view(self.export_pdf),
                 name="miscore_curriculumformanage_export_pdf"),
        ]
        return my + urls

    @transaction.atomic
    def manage_all(self, request):
        """
        Trang gộp: Chọn CTĐT → Thêm / Sửa ListCourse → Quan hệ học phần.
        Có hiển thị Tổng số tín chỉ ở tầng 2 (chỉ tính các dòng Active).
        """
        curriculum_id = request.GET.get("curriculum") or request.POST.get("curriculum")
        curricula = Curriculum.objects.select_related("major", "faculty").order_by("major__name", "-year")

        curriculum = None
        if curriculum_id:
            curriculum = get_object_or_404(
                Curriculum.objects.select_related("major", "faculty"),
                pk=curriculum_id
            )

        # --- POST actions ---
        if request.method == "POST" and curriculum:
            # Thêm dòng
            if "add_row" in request.POST:
                code = (request.POST.get("new_course_code") or "").strip().upper()
                sem = int(request.POST.get("new_semester_no") or 1)
                rqt = request.POST.get("new_requirement_type") or ListCourse.RequirementType.COMPULSORY
                cat = (request.POST.get("new_category") or "").strip()
                note = (request.POST.get("new_notes") or "").strip()
                act = bool(request.POST.get("new_is_active"))

                try:
                    course = Course.objects.get(code=code)
                except Course.DoesNotExist:
                    messages.error(request, f"Không tìm thấy học phần có mã: {code}")
                else:
                    obj, created = ListCourse.objects.get_or_create(
                        curriculum=curriculum, course=course,
                        defaults={
                            "semester_no": sem,
                            "requirement_type": rqt,
                            "category": cat,
                            "notes": note,
                            "is_active": act,
                        }
                    )
                    messages.success(request, f"{'Đã thêm' if created else 'Dòng đã tồn tại'}: {course.code} — {course.name}")

            # Lưu thay đổi / Xoá
            if "save_changes" in request.POST:
                ids = request.POST.getlist("row_id")
                to_delete = set(request.POST.getlist("delete_id"))
                for sid in ids:
                    try:
                        obj = ListCourse.objects.select_related("course").get(pk=int(sid), curriculum=curriculum)
                    except (ValueError, ListCourse.DoesNotExist):
                        continue
                    if sid in to_delete:
                        obj.delete()
                        continue
                    obj.semester_no = int(request.POST.get(f"semester_no_{sid}") or 1)
                    obj.requirement_type = request.POST.get(f"requirement_type_{sid}") or obj.requirement_type
                    obj.category = (request.POST.get(f"category_{sid}") or "").strip()
                    obj.notes = (request.POST.get(f"notes_{sid}") or "").strip()
                    obj.is_active = bool(request.POST.get(f"is_active_{sid}"))
                    obj.full_clean()
                    obj.save()
                messages.success(request, "Đã lưu thay đổi.")

            # Quan hệ học phần
            if "add_rel" in request.POST:
                main_id = request.POST.get("course_item")
                rel_id = request.POST.get("related_item")
                reltype = request.POST.get("relation_type")
                try:
                    main = ListCourse.objects.get(pk=main_id, curriculum=curriculum)
                    rel = ListCourse.objects.get(pk=rel_id, curriculum=curriculum)
                    ListCourseRelation.objects.create(
                        curriculum=curriculum, course_item=main, related_item=rel, relation_type=reltype
                    )
                    messages.success(request, "Đã thêm quan hệ.")
                except Exception as e:
                    messages.error(request, f"Lỗi khi thêm quan hệ: {e}")

            if "delete_rel" in request.POST:
                del_ids = request.POST.getlist("rel_id")
                ListCourseRelation.objects.filter(pk__in=del_ids, curriculum=curriculum).delete()
                messages.success(request, "Đã xoá quan hệ đã chọn.")

            return redirect(f"{reverse('admin:miscore_curriculumformanage_all')}?curriculum={curriculum.pk}")

        # --- Data render ---
        items = (ListCourse.objects.select_related("course")
                 .filter(curriculum=curriculum)
                 .order_by("semester_no", "course__code")) if curriculum else []

        relations = (ListCourseRelation.objects
                     .select_related("course_item__course", "related_item__course")
                     .filter(curriculum=curriculum)
                     .order_by("course_item__course__code", "relation_type", "related_item__course__code")) if curriculum else []

        totals = {"total_credits": Decimal("0")}
        if curriculum:
            totals = ListCourse.objects.filter(
                curriculum=curriculum, is_active=True
            ).aggregate(
                total_credits=Coalesce(Sum("course__credits"), Decimal("0"))
            )

        ctx = {
            "title": "Quản lý học phần CTĐT (gộp 3 tầng)",
            "curricula": curricula,
            "curriculum": curriculum,
            "items": items,
            "relations": relations,
            "opts": self.model._meta,
            "has_view_permission": True,
            **totals,
        }
        return render(request, "admin/miscore/lc_all.html", ctx)

    # ---------- PDF Export ----------
    def export_pdf(self, request):
        cid = request.GET.get("curriculum")
        if not cid:
            messages.error(request, "Thiếu tham số curriculum.")
            return redirect("admin:miscore_curriculumformanage_all")

        curriculum = get_object_or_404(
            Curriculum.objects.select_related("major", "faculty"),
            pk=cid
        )
        items = (ListCourse.objects
                .select_related("course")
                .filter(curriculum=curriculum)
                .order_by("semester_no", "course__code"))

        total_active = ListCourse.objects.filter(
            curriculum=curriculum, is_active=True
        ).aggregate(total_credits=Coalesce(Sum("course__credits"), Decimal("0")))["total_credits"] or Decimal("0")

        pdf = render_curriculum_pdf(curriculum, items, total_active)
        filename = f"CTDT_{curriculum.major}_{curriculum.year}.pdf".replace(" ", "_")
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f'inline; filename="{filename}"'
        return resp


# ================== Tuition ==================
@admin.register(Tuition)
class TuitionAdmin(admin.ModelAdmin):
    list_display = ("curriculum", "total_credits", "price_per_credit", "total_amount", "updated_at")
    list_select_related = ("curriculum",)
    search_fields = ("curriculum__major__name", "curriculum__major__code", "curriculum__faculty__name", "curriculum__year")
    autocomplete_fields = ("curriculum",)

    readonly_fields = ("total_credits", "total_amount", "updated_at", "computed_total_credits")
    fields = (
        "curriculum",
        "computed_total_credits",  # xem nhanh tổng tín tính trực tiếp
        "price_per_credit",
        "total_credits",
        "total_amount",
        "note",
        "updated_at",
    )

    # KHÔNG cho thêm mới (theo yêu cầu)
    def has_add_permission(self, request):
        return False

    def add_view(self, request, form_url='', extra_context=None):
        messages.info(request, "Không cho tạo mới học phí. Vào ‘Thay đổi’ để cập nhật.")
        return redirect('admin:miscore_tuition_changelist')

    # Tắt các nút add/change/delete cạnh field liên kết
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        fld = form.base_fields.get("curriculum")
        if fld and hasattr(fld, "widget"):
            w = fld.widget
            for attr in ("can_add_related", "can_change_related", "can_delete_related"):
                if hasattr(w, attr):
                    setattr(w, attr, False)
            if hasattr(w, "can_view_related"):
                w.can_view_related = True
        return form

    # Tổng tín tính trực tiếp (không lưu)
    def computed_total_credits(self, obj):
        if not obj or not obj.pk:
            return "—"
        return Tuition.calc_total_credits(obj.curriculum)
    computed_total_credits.short_description = "Tổng tín (tính trực tiếp)"

    # Action tính lại
    actions = ["recalculate"]

    def recalculate(self, request, queryset):
        cnt = 0
        for t in queryset:
            t.recalc()
            t.save(update_fields=["total_credits", "total_amount", "updated_at"])
            cnt += 1
        self.message_user(request, f"Đã tính lại {cnt} bản ghi.", level=messages.SUCCESS)
    recalculate.short_description = "Tính lại Tổng tín & Thành tiền"



# ================== User + Profile (Role) ==================
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fk_name = "user"
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    # Thêm cột hiển thị vai trò để dễ nhìn
    def role(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.get_role_display()
        return ""
    role.short_description = "Vai trò"

    list_display = BaseUserAdmin.list_display + ("role",)


# Hủy đăng ký User mặc định, đăng ký lại
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(CurriculumCopyTool)
class CurriculumCopyAdmin(admin.ModelAdmin):
    """
    Công cụ sao chép ListCourse từ CTĐT nguồn -> CTĐT đích.
    Là một mục riêng trên sidebar Admin.
    """
    # Ẩn nút “Thêm vào / Thay đổi”, chỉ hiển thị trang công cụ
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_view_permission(self, request, obj=None): return True

    # Khi bấm vào mục này (changelist), ta render luôn form sao chép
    def changelist_view(self, request, extra_context=None):
        return self.copy_view(request)

    def get_urls(self):
        """
        Gắn thêm 1 URL nội bộ cho trang công cụ (để reverse() / redirect cho sạch).
        """
        urls = super().get_urls()
        my = [
            path(
                "tool/",
                self.admin_site.admin_view(self.copy_view),
                name="miscore_curriculum_copy_tool",
            ),
        ]
        return my + urls

    @transaction.atomic
    def copy_view(self, request):
        """
        Form & xử lý sao chép danh sách học phần.
        """
        curricula = Curriculum.objects.select_related("major", "faculty").order_by("major__name", "-year")

        if request.method == "POST":
            src_id = request.POST.get("src_curriculum")
            dst_id = request.POST.get("dst_curriculum")
            clear  = bool(request.POST.get("clear_target"))

            if not src_id or not dst_id:
                messages.error(request, "Vui lòng chọn đầy đủ CTĐT nguồn và CTĐT đích.")
                return redirect(reverse("admin:miscore_curriculum_copy_tool"))

            if src_id == dst_id:
                messages.error(request, "CTĐT nguồn và đích không được trùng nhau.")
                return redirect(reverse("admin:miscore_curriculum_copy_tool"))

            src = get_object_or_404(Curriculum, pk=src_id)
            dst = get_object_or_404(Curriculum, pk=dst_id)

            if clear:
                ListCourse.objects.filter(curriculum=dst).delete()

            created = skipped = updated = 0

            for it in ListCourse.objects.select_related("course").filter(curriculum=src):
                obj, is_created = ListCourse.objects.get_or_create(
                    curriculum=dst,
                    course=it.course,
                    defaults={
                        "semester_no": it.semester_no,
                        "requirement_type": it.requirement_type,
                        "category": it.category,
                        "notes": it.notes,
                        "is_active": it.is_active,
                    }
                )
                if is_created:
                    created += 1
                else:
                    # Nếu muốn cập nhật khi đã tồn tại thì bỏ comment 6 dòng dưới:
                    # obj.semester_no      = it.semester_no
                    # obj.requirement_type = it.requirement_type
                    # obj.category         = it.category
                    # obj.notes            = it.notes
                    # obj.is_active        = it.is_active
                    # obj.save(); updated += 1
                    skipped += 1

            # Recalc học phí (nếu đã có bản ghi Tuition cho CTĐT đích)
            try:
                t = Tuition.objects.get(curriculum=dst)
                t.recalc()
                t.save()
            except Tuition.DoesNotExist:
                pass

            messages.success(
                request,
                f"Đã sao chép từ '{src}' → '{dst}'. "
                f"Thêm mới: {created}, Bỏ qua: {skipped}"
                + (f", Cập nhật: {updated}" if updated else "")
            )
            return redirect(reverse("admin:miscore_curriculum_copy_tool"))

        ctx = {
            "title": "Sao chép CTĐT",
            "curricula": curricula,
            "opts": CurriculumCopyTool._meta,   # để breadcrumb/title theo mục này
        }
        return render(request, "admin/miscore/curriculum_copy.html", ctx)
