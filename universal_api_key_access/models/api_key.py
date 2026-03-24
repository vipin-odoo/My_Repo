import secrets

from odoo import api, fields, models


class UniversalApiKey(models.Model):
    _name = "universal.api.key"
    _description = "Universal API Key"
    _rec_name = "name"

    name = fields.Char(required=True)
    user_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True)
    key = fields.Char(required=True, copy=False, readonly=True, index=True)
    active = fields.Boolean(default=True, index=True)

    @api.model
    def create_for_user(self, user):
        raw_key = secrets.token_urlsafe(40)
        self.create(
            {
                "name": f"Key for {user.login}",
                "user_id": user.id,
                "key": raw_key,
                "active": True,
            }
        )
        return {"raw_key": raw_key}

    @api.model
    def get_user_from_key(self, raw_key):
        key_record = self.search([("key", "=", raw_key), ("active", "=", True)], limit=1)
        return key_record.user_id if key_record else self.env["res.users"]
