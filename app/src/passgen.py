import base64
import hashlib

import numpy as np
from PIL import Image


def generate_password(image_path, key1, key2, key3, key4, password_length=16):
    with Image.open(image_path) as img:
        img_bytes = np.array(img).tobytes()
    combined_bytes = img_bytes + key1.encode('utf-8') + key2.encode('utf-8') + key3.encode('utf-8') + key4.encode(
        'utf-8')
    hash_object = hashlib.sha256(combined_bytes)
    hash_digest = hash_object.digest()
    base64_encoded = base64.urlsafe_b64encode(hash_digest).decode('utf-8')
    password = base64_encoded[:password_length].ljust(password_length, '0')
    return password


image_path = r'C:\Users\bogdanafter\Desktop\картиночки\860820.png'
key1 = '1-й ключ'
key2 = '2-й ключ'
key3 = '3-й ключ'
key4 = '4-й ключ'
password = generate_password(image_path, key1, key2, key3, key4)
print(f"Generated password: {password}")
