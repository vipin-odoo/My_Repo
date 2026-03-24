from odoo import http
from odoo.http import request


class UniversalApiController(http.Controller):

    @http.route("/api/auth/generate_key", type="json", auth="public", methods=["POST"], csrf=False, cors="*")
    def generate_key(self, **payload):
        user_id = payload.get("user_id")
        login = payload.get("login")

        if not user_id or not login:
            return {"ok": False, "error": "user_id and login are required"}

        user = request.env["res.users"].sudo().search([
            ("id", "=", user_id),
            ("login", "=", login),
            ("active", "=", True),
        ], limit=1)
        if not user:
            return {"ok": False, "error": "Invalid user_id/login combination"}

        key_result = request.env["universal.api.key"].sudo().create_for_user(user)
        api_key = key_result.key if hasattr(key_result, "key") else key_result.get("raw_key")

        return {
            "ok": True,
            "user_id": user.id,
            "login": user.login,
            "api_key": api_key,
        }

    @http.route("/api/model/read", type="json", auth="public", methods=["POST"], csrf=False, cors="*")
    def model_read(self, **payload):
        api_key = payload.get("api_key")
        model_name = payload.get("model")
        domain = payload.get("domain") or []
        fields_to_read = payload.get("fields")
        limit = payload.get("limit", 80)
        offset = payload.get("offset", 0)
        include_relations = payload.get("include_relations", True)
        max_depth = int(payload.get("max_depth", 1) or 1)

        if not api_key or not model_name:
            return {"ok": False, "error": "api_key and model are required"}

        user = request.env["universal.api.key"].sudo().get_user_from_key(api_key)
        if not user:
            return {"ok": False, "error": "Invalid API key"}

        if model_name not in request.env:
            return {"ok": False, "error": f"Model {model_name} not found"}

        model_env = request.env[model_name].sudo()
        if not fields_to_read:
            fields_to_read = list(model_env.fields_get().keys())

        records = model_env.search(domain, offset=offset, limit=limit)
        data = self._serialize_records(records, fields_to_read, include_relations, max_depth=max_depth)

        return {
            "ok": True,
            "user_id": user.id,
            "model": model_name,
            "count": len(records),
            "records": data,
        }

    def _serialize_records(self, records, field_names, include_relations, max_depth=1, _current_depth=0):
        result = []
        fields_meta = records.fields_get(field_names)

        for record in records:
            values = {}
            for field_name in field_names:
                if field_name not in fields_meta:
                    continue
                field_type = fields_meta[field_name]["type"]
                field_value = record[field_name]

                if field_type == "many2one":
                    values[field_name] = {
                        "id": field_value.id,
                        "display_name": field_value.display_name,
                    } if field_value else False
                elif field_type in ("one2many", "many2many"):
                    if include_relations and _current_depth < max_depth and field_value:
                        rel_field_names = list(field_value.fields_get().keys())
                        values[field_name] = self._serialize_records(
                            field_value,
                            rel_field_names,
                            include_relations,
                            max_depth=max_depth,
                            _current_depth=_current_depth + 1,
                        )
                    else:
                        values[field_name] = field_value.ids
                elif field_type in ("date", "datetime"):
                    values[field_name] = field_value.isoformat() if field_value else False
                else:
                    values[field_name] = field_value

            result.append(values)

        return result
