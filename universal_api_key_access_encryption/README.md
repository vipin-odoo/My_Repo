# Universal API Key Access - Encryption (Odoo 18)

This add-on extends `universal_api_key_access` with encrypted API key storage.

## What it changes

- API generation route remains the same: `POST /api/auth/generate_key` with `cors="*"`.
- Model read route remains the same: `POST /api/model/read` with `cors="*"`.
- Raw key is returned once to the client, but not stored in plain text.
- In database:
  - `universal.api.key.key` stores SHA-256 hash (used for lookup)
  - `universal.api.key.encrypted_key` stores Fernet-encrypted raw key

## Installation order

1. Install `universal_api_key_access`
2. Install `universal_api_key_access_encryption`

After installing the encryption add-on, newly generated keys are stored securely.
