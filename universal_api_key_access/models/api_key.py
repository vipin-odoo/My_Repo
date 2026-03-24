import hashlib
import secrets

from odoo import api, fields, models
from odoo.tools import config


class UniversalApiKey(models.Model):
    _name = "universal.api.key"
    _description = "Universal API Key"
    _rec_name = "name"

    name = fields.Char(required=True)
    user_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True)
    key_hash = fields.Char(required=True, copy=False, index=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("universal_api_key_hash_unique", "unique(key_hash)", "API key must be unique."),
    ]

    @api.model
    def _hash_key(self, raw_key):
        """One-way hash based on Odoo's database secret for secure key storage."""
        db_secret = (config.get("database_secret") or "").encode()
        return hashlib.pbkdf2_hmac(
            "sha256",
            raw_key.encode(),
            db_secret,
            600_000,
        ).hex()

    @api.model
    def create_for_user(self, user):
        raw_key = secrets.token_urlsafe(40)
        key_record = self.create(
            {
                "name": f"Key for {user.login}",
                "user_id": user.id,
                "key_hash": self._hash_key(raw_key),
                "active": True,
            }
        )
        return key_record, raw_key

    @api.model
    def get_user_from_key(self, raw_key):
        key_hash = self._hash_key(raw_key)
        key_record = self.search([("key_hash", "=", key_hash), ("active", "=", True)], limit=1)
        return key_record.user_id if key_record else self.env["res.users"]
