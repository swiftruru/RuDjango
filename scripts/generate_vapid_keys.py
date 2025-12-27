#!/usr/bin/env python
"""
生成 Web Push 所需的 VAPID keys
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

# 生成私鑰
private_key = ec.generate_private_key(
    ec.SECP256R1(),
    default_backend()
)

# 獲取公鑰
public_key = private_key.public_key()

# 序列化私鑰
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

# 序列化公鑰
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# 轉換為 base64url 格式（用於前端）
public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)
public_key_base64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')

print("=" * 70)
print("VAPID Keys 已生成")
print("=" * 70)
print()
print("請將以下內容添加到 settings.py 或 .env 文件:")
print()
print("# VAPID Private Key (PEM 格式，後端使用)")
print("VAPID_PRIVATE_KEY = '''")
print(private_pem.decode())
print("'''")
print()
print("# VAPID Public Key (PEM 格式，後端使用)")
print("VAPID_PUBLIC_KEY_PEM = '''")
print(public_pem.decode())
print("'''")
print()
print("# VAPID Public Key (Base64URL 格式，前端使用)")
print(f"VAPID_PUBLIC_KEY = '{public_key_base64}'")
print()
print("=" * 70)
print("⚠️  請妥善保管私鑰，不要提交到版本控制系統！")
print("=" * 70)
