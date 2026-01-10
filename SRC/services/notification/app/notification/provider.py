import logging

logger = logging.getLogger(__name__)

def send_mock(channel: str, to: str, subject: str, body: str):
    # Mock provider: log and return response
    logger.info(f"[MOCK_PROVIDER] channel={channel} to={to} subject={subject}")
    return {"provider": "mock", "channel": channel, "to": to, "accepted": True}
