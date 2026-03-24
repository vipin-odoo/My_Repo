import base64
import hashlib
import secrets

from cryptography.fernet import Fernet, InvalidToken

from odoo import api, fields, models


class UniversalApiKeyEncrypted(models.Model):
    _inherit = "universal.api.key"

    encrypted_key = fields.Text(copy=False, readonly=True)

    @api.model
    def _encryption_secret(self):
        """Build a stable Fernet secret from database.secret."""
        db_secret = (
            self.env["ir.config_parameter"].sudo().get_param("database.secret") or "odoo-universal-api"
        )
        digest = hashlib.sha256(db_secret.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    @api.model
    def _fernet(self):
        return Fernet(self._encryption_secret())

    @api.model
    def _hash_key(self, raw_key):
        return hashlib.sha256((raw_key or "").encode("utf-8")).hexdigest()

    @api.model
    def create_for_user(self, user):
        raw_key = secrets.token_urlsafe(40)
        key_hash = self._hash_key(raw_key)
        encrypted_key = self._fernet().encrypt(raw_key.encode("utf-8")).decode("utf-8")

        self.create(
            {
                "name": f"Encrypted key for {user.login}",
                "user_id": user.id,
                "key": key_hash,
                "encrypted_key": encrypted_key,
                "active": True,
            }
        )
        return {"raw_key": raw_key}

    @api.model
    def get_user_from_key(self, raw_key):
        key_hash = self._hash_key(raw_key)
        key_record = self.search([("key", "=", key_hash), ("active", "=", True)], limit=1)
        if not key_record:
            return self.env["res.users"]

        # Extra integrity check: confirm encrypted payload maps back to the provided raw key.
        if key_record.encrypted_key:
            try:
                decrypted = self._fernet().decrypt(key_record.encrypted_key.encode("utf-8")).decode("utf-8")
            except (InvalidToken, ValueError):
                return self.env["res.users"]
            if decrypted != raw_key:
                return self.env["res.users"]

        return key_record.user_id
