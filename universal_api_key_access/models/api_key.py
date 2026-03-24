


class UniversalApiKey(models.Model):
    _name = "universal.api.key"
    _description = "Universal API Key"
    _rec_name = "name"

    name = fields.Char(required=True)
    user_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True)
    def create_for_user(self, user):
        raw_key = secrets.token_urlsafe(40)
        key_record = self.create(
            {
                "name": f"Key for {user.login}",
                "user_id": user.id,

        return key_record.user_id if key_record else self.env["res.users"]
