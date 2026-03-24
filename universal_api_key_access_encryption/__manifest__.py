{
    "name": "Universal API Key Access - Encryption",
    "version": "18.0.1.0.0",
    "summary": "Encrypt and hash Universal API keys for safer storage",
    "description": """
Adds a security layer on top of Universal API Key Access:
- stores only SHA-256 hash for key lookup
- stores encrypted key payload using Fernet
- keeps public JSON routes with cors='*'
""",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["base", "universal_api_key_access"],
    "data": [],
    "installable": True,
    "application": False,
}
