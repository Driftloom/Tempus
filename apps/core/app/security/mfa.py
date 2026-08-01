"""Multi-Factor Authentication (MFA)."""

import base64
from io import BytesIO

import pyotp
import qrcode
import structlog

logger = structlog.get_logger(__name__)


class MFAManager:
    """Manager for Multi-Factor Authentication."""

    def __init__(self) -> None:
        """Initialize MFA manager."""
        self.issuer = "TEMPUS"

    def generate_secret(self) -> str:
        """Generate TOTP secret."""
        return pyotp.random_base32()

    def generate_totp_uri(
        self,
        secret: str,
        user_email: str
    ) -> str:
        """Generate TOTP URI for QR code."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer
        )

    def generate_qr_code(self, uri: str) -> str:
        """Generate QR code as base64 image."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)

    def setup_mfa(self, user_email: str) -> dict[str, str]:
        """Setup MFA for user."""
        secret = self.generate_secret()
        uri = self.generate_totp_uri(secret, user_email)
        qr_code = self.generate_qr_code(uri)

        return {
            "secret": secret,
            "qr_code": qr_code,
            "uri": uri,
        }

    def verify_mfa_setup(self, secret: str, token: str) -> bool:
        """Verify MFA during setup."""
        return self.verify_totp(secret, token)


class RecoveryCodeManager:
    """Manager for MFA recovery codes."""

    def __init__(self):
        """Initialize recovery code manager."""
        self.code_length = 10
        self.num_codes = 10

    def generate_recovery_codes(self) -> list[str]:
        """Generate recovery codes."""
        import secrets
        codes = []
        for _ in range(self.num_codes):
            code = secrets.token_hex(self.code_length // 2).upper()
            codes.append(code)
        return codes

    def verify_recovery_code(self, code: str, used_codes: list[str]) -> bool:
        """Verify recovery code."""
        code_upper = code.upper()
        if code_upper in used_codes:
            return False
        return len(code) == self.code_length and code.isalnum()


# Global instances
mfa_manager = MFAManager()
recovery_code_manager = RecoveryCodeManager()
