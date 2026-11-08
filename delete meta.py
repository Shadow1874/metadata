import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from PIL.ExifTags import TAGS
import os
import logging
from datetime import datetime

# --- Настройка логирования ---
# Логи сохраняются в файл app_log.txt в той же папке, где запущен скрипт
log_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_log.txt")
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)


class MetadataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Удаление метаданных")
        self.root.geometry("800x580")
        self.root.minsize(650, 450)
        self.root.configure(bg="#F3F5F9")

        self.file_path = None
        logging.info("Приложение успешно запущено.")

        # --- Цветовая схема ---
        bg_color = "#F3F5F9"
        card_color = "#FFFFFF"
        text_color = "#1E293B"
        secondary_color = "#64748B"
        accent_color = "#2563EB"
        success_color = "#16A34A"
        danger_color = "#DC2626"

        # --- Настройка стилей ttk ---
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview",
            background="#FFFFFF",
            foreground=text_color,
            fieldbackground="#FFFFFF",
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )

        style.configure(
            "Custom.Treeview.Heading",
            background="#F1F5F9",
            foreground="#475569",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 12),
            borderwidth=0
        )

        style.map(
            "Custom.Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", "#1E40AF")]
        )

        style.configure(
            "Custom.Vertical.TScrollbar",
            background="#CBD5E1",
            troughcolor="#F1F5F9",
            borderwidth=0,
            arrowsize=12
        )

        # --- Основной контейнер ---
        main_frame = tk.Frame(root, bg=bg_color, padx=25, pady=22)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Заголовок ---
        header_frame = tk.Frame(main_frame, bg=bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 22))

        tk.Label(
            header_frame,
            text="Удаление метаданных",
            font=("Segoe UI", 21, "bold"),
            fg=text_color,
            bg=bg_color
        ).pack(anchor=tk.W, pady=(4, 2))

        tk.Label(
            header_frame,
            text="Просмотр информации об изображениях и очистка EXIF-данных",
            font=("Segoe UI", 10),
            fg=secondary_color,
            bg=bg_color
        ).pack(anchor=tk.W)

        # --- Панель управления ---
        top_frame = tk.Frame(
            main_frame,
            bg=card_color,
            padx=16,
            pady=15,
            highlightthickness=1,
            highlightbackground="#E2E8F0"
        )
        top_frame.pack(fill=tk.X, pady=(0, 18))

        self.btn_open = tk.Button(
            top_frame,
            text="  Открыть изображение  ",
            command=self.open_file,
            bg=accent_color,
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2"
        )
        self.btn_open.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_clear = tk.Button(
            top_frame,
            text="  Удалить метаданные  ",
            command=self.clear_metadata,
            bg=danger_color,
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.btn_clear.pack(side=tk.LEFT)

        self.lbl_status = tk.Label(
            top_frame,
            text="Файл не выбран",
            fg=secondary_color,
            bg="#F1F5F9",
            font=("Segoe UI", 9),
            padx=12,
            pady=8
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=(10, 0))

        # --- Заголовок таблицы ---
        table_header = tk.Frame(main_frame, bg=bg_color)
        table_header.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            table_header,
            text="Информация об изображении",
            font=("Segoe UI", 13, "bold"),
            fg=text_color,
            bg=bg_color
        ).pack(side=tk.LEFT)

        tk.Label(
            table_header,
            text="Свойства и EXIF",
            font=("Segoe UI", 9),
            fg=secondary_color,
            bg=bg_color
        ).pack(side=tk.RIGHT)

        # --- Контейнер таблицы ---
        table_frame = tk.Frame(
            main_frame,
            bg=card_color,
            padx=10,
            pady=10,
            highlightthickness=1,
            highlightbackground="#E2E8F0"
        )
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("tag", "value")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )

        self.tree.heading("tag", text="Тег / Свойство")
        self.tree.heading("value", text="Значение")

        self.tree.column(
            "tag",
            width=200,
            minwidth=150,
            anchor=tk.W
        )

        self.tree.column(
            "value",
            width=450,
            minwidth=200,
            anchor=tk.W
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
            style="Custom.Vertical.TScrollbar"
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Нижняя панель ---
        footer_frame = tk.Frame(main_frame, bg=bg_color)
        footer_frame.pack(fill=tk.X, pady=(12, 0))

        tk.Label(
            footer_frame,
            text="Работа с изображениями происходит локально",
            font=("Segoe UI", 9),
            fg=secondary_color,
            bg=bg_color
        ).pack(side=tk.LEFT)

        tk.Label(
            footer_frame,
            text="Metadata Cleaner",
            font=("Segoe UI", 9, "bold"),
            fg="#94A3B8",
            bg=bg_color
        ).pack(side=tk.RIGHT)

    def open_file(self):
        file_types = [("Изображения", "*.jpg *.jpeg *.png *.tiff")]
        path = filedialog.askopenfilename(title="Выберите изображение", filetypes=file_types)

        if not path:
            return

        self.file_path = path
        filename = os.path.basename(path)
        self.lbl_status.config(text=f"Файл: {filename}", fg="black")

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            img = Image.open(self.file_path)
            exif_data = img._getexif()

            if exif_data:
                tags_found = 0
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode(errors="ignore")
                        except:
                            value = "[Байтовые данные]"
                    self.tree.insert("", tk.END, values=(tag_name, str(value)))
                    tags_found += 1

                self.btn_clear.config(state=tk.NORMAL)
                logging.info(f"Успешно открыт файл: {filename}. Найдено тегов EXIF: {tags_found}")
            else:
                self.tree.insert("", tk.END, values=("Информация", "Метаданные EXIF не найдены или файл чист."))
                self.btn_clear.config(state=tk.DISABLED)
                logging.info(f"Файл открыт, но метаданные отсутствуют: {filename}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            self.btn_clear.config(state=tk.DISABLED)
            logging.error(f"Ошибка при чтении файла {filename}: {str(e)}")

    def clear_metadata(self):
        if not self.file_path:
            return

        orig_dir, orig_name = os.path.split(self.file_path)
        name, ext = os.path.splitext(orig_name)
        suggested_name = f"{name}_clean{ext}"

        save_path = filedialog.asksaveasfilename(
            title="Сохранить очищенный файл",
            initialdir=orig_dir,
            initialfile=suggested_name,
            filetypes=[("Изображение", f"*{ext}")]
        )

        if not save_path:
            return

        try:
            img = Image.open(self.file_path)
            data = list(img.getdata())
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(data)
            clean_img.save(save_path)

            messagebox.showinfo("Успех", f"Файл успешно сохранен без метаданных:\n{save_path}")
            logging.info(f"Метаданные удалены. Исходный: {orig_name} -> Очищенный: {os.path.basename(save_path)}")

            self.file_path = None
            self.lbl_status.config(text="Файл очищен и сохранен", fg="green")
            self.btn_clear.config(state=tk.DISABLED)
            for item in self.tree.get_children():
                self.tree.delete(item)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось очистить метаданные:\n{e}")
            logging.error(f"Не удалось очистить файл {orig_name}: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MetadataApp(root)
    root.mainloop()
