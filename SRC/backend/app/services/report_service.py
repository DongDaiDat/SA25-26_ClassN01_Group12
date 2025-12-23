import os
import uuid
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from docxtpl import DocxTemplate
from app.core.config import settings
from app.db.models import ProgramVersion, Program, ReportTemplate, FileAsset, ReportExport
from app.utils.libreoffice import convert_docx_to_pdf
from app.services.audit_service import write_audit

async def export_moet(db: AsyncSession, actor_id: uuid.UUID, program_version_id: uuid.UUID, template_code: str) -> dict:
    pv = (await db.execute(select(ProgramVersion).where(ProgramVersion.program_version_id == program_version_id))).scalars().first()
    if not pv:
        raise ValueError("PROGRAM_VERSION_NOT_FOUND")

    prog = (await db.execute(select(Program).where(Program.program_id == pv.program_id))).scalars().first()
    if not prog:
        raise ValueError("PROGRAM_NOT_FOUND")

    tpl = (await db.execute(select(ReportTemplate).where(
        ReportTemplate.template_code == template_code,
        ReportTemplate.is_active == True
    ))).scalars().first()  # noqa
    if not tpl:
        raise ValueError("TEMPLATE_NOT_FOUND")

    tpl_file = (await db.execute(select(FileAsset).where(FileAsset.file_id == tpl.file_id))).scalars().first()
    if not tpl_file:
        raise ValueError("TEMPLATE_FILE_NOT_FOUND")

    # dataset MVP (bạn mở rộng lấy PLO/CLO/Curriculum...)
    context = {
        "program_code": prog.program_code,
        "program_name_vi": prog.name_vi,
        "program_name_en": prog.name_en,
        "apply_year": pv.apply_year,
        "watermark": "NỘI BỘ" if pv.state != "ACTIVE" else "",
    }

    doc = DocxTemplate(tpl_file.storage_path)
    doc.render(context)

    out_dir = settings.report_output_dir
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    docx_path = os.path.join(out_dir, f"MOET_{prog.program_code}_{pv.apply_year}_{uuid.uuid4().hex}.docx")
    doc.save(docx_path)

    pdf_path = convert_docx_to_pdf(docx_path, out_dir)

    # lưu file record
    docx_asset = FileAsset(
        file_name=os.path.basename(docx_path),
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        size=os.path.getsize(docx_path),
        storage_path=docx_path,
        uploaded_by=actor_id,
    )
    pdf_asset = FileAsset(
        file_name=os.path.basename(pdf_path),
        mime_type="application/pdf",
        size=os.path.getsize(pdf_path),
        storage_path=pdf_path,
        uploaded_by=actor_id,
    )
    db.add_all([docx_asset, pdf_asset])
    await db.commit()

    export = ReportExport(
        template_id=tpl.template_id,
        program_version_id=pv.program_version_id,
        output_docx_file_id=docx_asset.file_id,
        output_pdf_file_id=pdf_asset.file_id,
        exported_by=actor_id,
    )
    db.add(export)
    await db.commit()

    await write_audit(db, actor_id=actor_id, action="EXPORT_MOET", object_type="ProgramVersion", object_id=program_version_id,
                      after_data={"template_code": template_code})

    return {"docx_path": docx_path, "pdf_path": pdf_path}

async def upload_template(
    db: AsyncSession,
    actor_id: uuid.UUID,
    template_code: str,
    name: str,
    version: int,
    storage_path: str,
    file_name: str,
    mime_type: str,
    size: int,
) -> dict:
    """
    Lưu template MOET (.docx) vào DB:
    - tạo FileAsset trỏ tới storage_path (file đã được endpoint lưu sẵn)
    - tạo ReportTemplate active
    - deactivate các template active cũ cùng template_code (đảm bảo 1 bản active)
    """

    # 1) Tạo record FileAsset cho file template
    file_asset = FileAsset(
        file_name=file_name,
        mime_type=mime_type,
        size=size,
        storage_path=storage_path,
        uploaded_by=actor_id,
    )
    db.add(file_asset)
    await db.flush()  # lấy file_id

    # 2) Nếu đã có template cùng code+version -> báo lỗi rõ ràng
    existed = (
        await db.execute(
            select(ReportTemplate).where(
                ReportTemplate.template_code == template_code,
                ReportTemplate.version == version,
            )
        )
    ).scalars().first()
    if existed:
        raise ValueError("TEMPLATE_VERSION_ALREADY_EXISTS")

    # 3) Deactivate các template đang active cùng template_code (nếu có)
    old_active = (
        await db.execute(
            select(ReportTemplate).where(
                ReportTemplate.template_code == template_code,
                ReportTemplate.is_active == True,  # noqa
            )
        )
    ).scalars().all()
    for t in old_active:
        t.is_active = False

    # 4) Tạo template mới active
    tpl = ReportTemplate(
        template_code=template_code,
        name=name,
        version=version,
        file_id=file_asset.file_id,
        is_active=True,
    )
    db.add(tpl)

    await db.commit()
    await db.refresh(tpl)

    # 5) Audit
    await write_audit(
        db,
        actor_id=actor_id,
        action="UPLOAD_TEMPLATE",
        object_type="ReportTemplate",
        object_id=tpl.template_id,
        after_data={
            "template_code": template_code,
            "name": name,
            "version": version,
            "file_name": file_name,
        },
    )

    return {
        "template_id": str(tpl.template_id),
        "template_code": template_code,
        "name": name,
        "version": version,
        "file_id": str(file_asset.file_id),
        "storage_path": storage_path,
        "is_active": True,
    }
