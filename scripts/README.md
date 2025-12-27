# Scripts Directory

This directory contains utility scripts for the RuDjango project.

## Available Scripts

### `generate_vapid_keys.py`

**Purpose**: Generate new VAPID (Voluntary Application Server Identification) keys for Web Push notifications.

**Usage**:
```bash
python scripts/generate_vapid_keys.py
```

**When to use**:
- Setting up a new development/production environment
- Rotating keys after a security incident
- Generating keys for testing purposes

**Output**:
The script will output three values that should be added to your `.env` file:
- `VAPID_PRIVATE_KEY` - Private key (PEM format, backend use)
- `VAPID_PUBLIC_KEY_PEM` - Public key (PEM format, backend use)
- `VAPID_PUBLIC_KEY` - Public key (Base64URL format, frontend use)

**⚠️ Security Note**:
- Never commit the generated private key to version control
- Always store keys in `.env` file (which is gitignored)
- Rotate keys immediately if compromised

## Adding New Scripts

When adding new utility scripts to this directory:

1. Add clear documentation in this README
2. Include usage examples
3. Add appropriate error handling
4. Consider adding the script to `.gitignore` if it contains sensitive logic
