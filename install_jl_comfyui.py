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

def update_progress(step, total_steps):
    progress_bar['value'] = (step / total_steps) * 100
    progress_label.config(text=f"Прогресс: {int(progress_bar['value'])}%")
    window.update_idletasks()

def run_command(command, message):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for line in process.stdout:
        log_text.insert(tk.END, line)
        log_text.see(tk.END)
        window.update_idletasks()
    return_code = process.wait()
    if return_code != 0:
        error_output = process.stderr.read()
        log_text.insert(tk.END, f"Ошибка при выполнении команды: {message}\n")
        log_text.insert(tk.END, f"Вывод ошибки: {error_output}\n")
        messagebox.showerror("Ошибка", f"Не удалось выполнить: {message}\nВывод ошибки: {error_output}")
        install_button.config(state=tk.NORMAL)
        raise Exception(f"Ошибка при выполнении команды: {message}")
    else:
        log_text.insert(tk.END, f"{message} завершено.\n")

def install():
    archive_path = archive_entry.get()
    install_path = install_entry.get()

    if not archive_path or not install_path:
        messagebox.showerror("Ошибка", "Пожалуйста, укажите путь к архиву и путь установки.")
        return

    if not os.path.isfile(archive_path):
        messagebox.showerror("Ошибка", f"Указанный архив не существует: {archive_path}")
        return

    install_button.config(state=tk.DISABLED)
    log_text.delete('1.0', tk.END)
    progress_bar['value'] = 0
    total_steps = 5
    current_step = 0

    log_text.insert(tk.END, "Начинаем установку ComfyUI...\n")

    try:
        # Проверка наличия WinRAR и установка при необходимости
        current_step += 1
        update_progress(current_step, total_steps)
        try:
            subprocess.call(["C:\\Program Files\\WinRAR\\winrar.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            log_text.insert(tk.END, "WinRAR не найден. Устанавливаем WinRAR...\n")
            winrar_path = resource_path("WinRAR.v5.01.exe")
            run_command([winrar_path, "/S"], "Установка WinRAR")

        # Проверка наличия Python и установка при необходимости
        current_step += 1
        update_progress(current_step, total_steps)
        try:
            subprocess.call(["C:\\Program Files\\Python310\\python.exe", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            log_text.insert(tk.END, "Python не найден. Устанавливаем Python...\n")
            python_path = resource_path("python-3.10.6-amd64.exe")
            run_command([python_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"], "Установка Python")

        # Распаковка архива
        current_step += 1
        update_progress(current_step, total_steps)
        log_text.insert(tk.END, "Распаковка архива...\n")
        run_command(["C:\\Program Files\\WinRAR\\winrar.exe", "x", archive_path, install_path], "Распаковка архива")

        # Добавление путей в системную переменную PATH
        current_step += 1
        update_progress(current_step, total_steps)
        python_path = os.path.join(install_path, "python")
        ffmpeg_path = os.path.join(install_path, "ffmpeg", "bin")
        os.environ["PATH"] += f";{python_path};{python_path}\\Scripts;{ffmpeg_path}"

        # Обновление ComfyUI
        current_step += 1
        update_progress(current_step, total_steps)
        log_text.insert(tk.END, "Обновление ComfyUI...\n")
        update_path = os.path.join(install_path, "update")
        run_command(["update_comfyui.bat"], "Обновление ComfyUI")

        install_button.config(state=tk.NORMAL)
        messagebox.showinfo("Успех", "Установка ComfyUI завершена успешно!")
    except Exception as e:
        log_text.insert(tk.END, f"Ошибка при установке ComfyUI: {str(e)}\n")
        messagebox.showerror("Ошибка", f"Не удалось установить ComfyUI. Ошибка: {str(e)}")
        install_button.config(state=tk.NORMAL)

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

progress_bar = ttk.Progressbar(frame, mode='determinate', length=300)
progress_bar.grid(row=3, column=0, columnspan=3, pady=(10, 0))

progress_label = ttk.Label(frame, text="Прогресс: 0%")
progress_label.grid(row=4, column=0, columnspan=3)

log_text = tk.Text(frame, height=10, width=60)
log_text.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

window.mainloop()
