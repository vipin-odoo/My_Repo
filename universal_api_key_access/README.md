# Universal API Key Access (Odoo 18)

This module adds two JSON routes with `cors="*"`:

1. `POST /api/auth/generate_key`
   - Input: `user_id`, `login`
   - Output: generated API key for that user.

2. `POST /api/model/read`
   - Input: `api_key`, `model`, optional `domain`, `fields`, `limit`, `offset`, `include_relations`, `max_depth`
   - Output: record values for any model. For one2many/many2many, it can include nested record values.

## Example payloads

Generate key:

```json
{
  "user_id": 2,
  "login": "admin"
}
```

Read `account.move` and include line values:

```json
{
  "api_key": "PASTE_KEY",
  "model": "account.move",
  "domain": [["id", ">", 0]],
  "fields": ["name", "partner_id", "line_ids", "invoice_line_ids"],
  "include_relations": true,
  "max_depth": 2
}
```
