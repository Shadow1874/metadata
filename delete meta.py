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
        self.root.geometry("600x500") 
        self.root.minsize(500, 400)
        
        self.file_path = None
        logging.info("Приложение успешно запущено.")
        
        # --- Верхняя панель управления ---
        top_frame = tk.Frame(root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        
        self.btn_open = tk.Button(top_frame, text="Открыть изображение", command=self.open_file, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.btn_open.pack(side=tk.LEFT, padx=5)
        
        self.btn_clear = tk.Button(top_frame, text="Удалить метаданные", command=self.clear_metadata, bg="#f44336", fg="white", font=("Arial", 10, "bold"), state=tk.DISABLED)
        self.btn_clear.pack(side=tk.LEFT, padx=5)
        
        self.lbl_status = tk.Label(top_frame, text="Файл не выбран", fg="gray", font=("Arial", 9, "italic"))
        self.lbl_status.pack(side=tk.LEFT, padx=10)
        
        # --- Таблица для отображения метаданных ---
        table_frame = tk.Frame(root, padx=10, pady=5)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("tag", "value")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("tag", text="Тег / Свойство")
        self.tree.heading("value", text="Значение")
        self.tree.column("tag", width=200, anchor=tk.W)
        self.tree.column("value", width=350, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
