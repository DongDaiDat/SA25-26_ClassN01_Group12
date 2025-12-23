import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings

async def send_email(to: str, subject: str, html: str) -> None:
    msg = EmailMessage()
    msg["From"] = f"{settings.mail_from_name} <{settings.mail_from_address or settings.mail_username}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content("Email này yêu cầu trình đọc HTML.")
    msg.add_alternative(html, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=settings.mail_host,
        port=settings.mail_port,
        start_tls=settings.mail_use_tls,
        username=settings.mail_username,
        password=settings.mail_app_password,
        timeout=15,
    )
