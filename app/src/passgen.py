import base64
import hashlib
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import numpy as np
from PIL import Image


def generate_password(image_path, password_length=16):
    with Image.open(image_path) as img:
        img_bytes = np.array(img).tobytes()
    combined_bytes = img_bytes
    hash_object = hashlib.sha256(combined_bytes)
    hash_digest = hash_object.digest()
    base64_encoded = base64.urlsafe_b64encode(hash_digest).decode('utf-8')
    password = base64_encoded[:password_length].ljust(password_length, '0')
    return password


def open_file_dialog():
    file_path = filedialog.askopenfilename()
    if file_path:
        password = generate_password(file_path)
        result_label.config(text=password)


okno = Tk()
okno.title("Генератор паролей по картинке")
okno.geometry("250x100")

open_button = ttk.Button(text="Открыть файл", command=lambda: open_file_dialog())
open_button.grid(column=0, row=1, sticky=NSEW, padx=10)

copy_button = ttk.Button(text="Копировать пароль", command=lambda: okno.clipboard_append(result_label.cget("text")))
copy_button.grid(column=1, row=1, sticky=NSEW, padx=10)

result_label = ttk.Label(okno, text="")
result_label.grid(column=0, row=2, columnspan=2, sticky=NSEW, padx=10)

okno.mainloop()




