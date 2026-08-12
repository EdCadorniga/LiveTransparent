import base64
import hashlib
import os
from Crypto.Cipher import AES

key_hex = os.environ.get("N8N_ENCRYPTION_KEY", "")
encrypted = os.environ.get("N8N_ENCRYPTED_CREDENTIAL", "")
if not key_hex or not encrypted:
    raise SystemExit("Set N8N_ENCRYPTION_KEY and N8N_ENCRYPTED_CREDENTIAL before running")

# n8n uses CryptoJS which uses OpenSSL-compatible key derivation
# Key = SHA256(encryption_key), IV = first 16 bytes of decrypted data after salt
raw = base64.b64decode(encrypted)

# CryptoJS uses "Salted__" + 8-byte salt + ciphertext
salt = raw[8:16]
ciphertext = raw[16:]

# Derive key and IV using OpenSSL EVP_BytesToKey (MD5 based)
password = key_hex.encode('utf-8')
key_material = b''
prev = b''
while len(key_material) < 48:  # 32 key + 16 IV
    prev = hashlib.md5(prev + password + salt).digest()
    key_material += prev

aes_key = key_material[:32]
aes_iv = key_material[32:48]

cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
plaintext = cipher.decrypt(ciphertext)

# Remove PKCS7 padding
pad_len = plaintext[-1]
plaintext = plaintext[:-pad_len]

print(plaintext.decode('utf-8'))
