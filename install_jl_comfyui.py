import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def select_archive():
    archive_path = filedialog.askopenfilename(filetypes=[("RAR Files", "*.rar")])
    archive_entry.delete(0, tk.END)
    archive_entry.insert(0, archive_path)

def install():
    archive_path = archive_entry.get()
    install_path = install_entry.get()

    if not archive_path or not install_path:
        messagebox.showerror("Ошибка", "Пожалуйста, укажите путь к архиву и путь установки.")
        return

    install_button.config(state=tk.DISABLED)
    progress_bar.start()

    log_text.insert(tk.END, "Начинаем установку ComfyUI...\n")

    # Проверка наличия WinRAR и установка при необходимости
    try:
        subprocess.call(["winrar"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        log_text.insert(tk.END, "WinRAR не найден. Устанавливаем WinRAR...\n")
        winrar_path = resource_path("WinRAR.v5.01.exe")
        subprocess.call([winrar_path, "/S"])
        log_text.insert(tk.END, "WinRAR установлен.\n")

    # Проверка наличия Python и установка при необходимости
    try:
        subprocess.call(["python", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        log_text.insert(tk.END, "Python не найден. Устанавливаем Python...\n")
        python_path = resource_path("python-3.10.6-amd64.exe")
        subprocess.call([python_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
        log_text.insert(tk.END, "Python установлен.\n")

    # Распаковка архива
    log_text.insert(tk.END, "Распаковка архива...\n")
    subprocess.call(["winrar", "x", archive_path, install_path])
    log_text.insert(tk.END, "Архив распакован.\n")

    # Добавление путей в системную переменную PATH
    python_path = os.path.join(install_path, "python")
    ffmpeg_path = os.path.join(install_path, "ffmpeg", "bin")
    os.environ["PATH"] += f";{python_path};{python_path}\\Scripts;{ffmpeg_path}"

    # Обновление ComfyUI
    log_text.insert(tk.END, "Обновление ComfyUI...\n")
    update_path = os.path.join(install_path, "update")
    subprocess.call(["update_comfyui.bat"], cwd=update_path, shell=True)
    log_text.insert(tk.END, "Обновление ComfyUI завершено.\n")

    progress_bar.stop()
    install_button.config(state=tk.NORMAL)
    messagebox.showinfo("Успех", "Установка ComfyUI завершена успешно!")

# Создание графического интерфейса
window = tk.Tk()
window.title("Установка ComfyUI")

frame = ttk.Frame(window, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

archive_label = ttk.Label(frame, text="Путь к архиву JL_ComfyUI.rar:")
archive_label.grid(row=0, column=0, sticky=tk.W)

archive_entry = ttk.Entry(frame, width=50)
archive_entry.grid(row=0, column=1, padx=(5, 0))

archive_button = ttk.Button(frame, text="Выбрать", command=select_archive)
archive_button.grid(row=0, column=2, padx=(5, 0))

install_label = ttk.Label(frame, text="Путь установки:")
install_label.grid(row=1, column=0, sticky=tk.W)

install_entry = ttk.Entry(frame, width=50)
install_entry.insert(0, "C:\\Ai\\JL\\JL_ComfyUI")
install_entry.grid(row=1, column=1, padx=(5, 0))

install_button = ttk.Button(frame, text="Установить", command=install)
install_button.grid(row=2, column=1, pady=(10, 0))

progress_bar = ttk.Progressbar(frame, mode='indeterminate')
progress_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

log_text = tk.Text(frame, height=10, width=60)
log_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

window.mainloop()