import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".doc"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programs": [".exe", ".bat", ".msi", ".sh"],
    "Others": []  # Any uncategorized files
}
class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("1000x700")
        # Add directory section
        ttk.Label(root, text="Select Directories to Organize:").pack(pady=5)
        self.directory_list = []
        self.directory_frame = ttk.Frame(root)
        self.directory_frame.pack(fill="both", expand=True, padx=10, pady=5)
        ttk.Button(root, text="Add Directory", command=self.add_directory).pack(pady=5)
        ttk.Button(root, text="Start Organizing", command=self.start_organizing).pack(pady=5)
        # Tabs for organized files
        self.tab_control = ttk.Notebook(root)
        self.tab_control.pack(fill="both", expand=True, padx=10, pady=5)
    def add_directory(self):
        """Allow user to add a directory to be organized."""
        directory = filedialog.askdirectory(title="Select Directory")
        if directory and directory not in self.directory_list:
            self.directory_list.append(directory)
            label = tk.Label(self.directory_frame, text=directory, anchor="w", bg="#eaeaea")
            label.pack(fill="x", padx=5, pady=2)
    def start_organizing(self):
        """Start organizing the selected directories."""
        if not self.directory_list:
            messagebox.showerror("Error", "Please add at least one directory to organize.")
            return
        for directory in self.directory_list:
            threading.Thread(target=self.organize_and_update_gui, args=(directory,), daemon=True).start()
    def organize_and_update_gui(self, directory):
        """Organize files and update the GUI."""
        organized_files = self.organize_files(directory)
        tab = ttk.Frame(self.tab_control)
        self.tab_control.add(tab, text=os.path.basename(directory))
        self.update_tab_content(tab, organized_files)
    def organize_files(self, directory):
        """Organizes files in a directory and its subdirectories."""
        organized_files = {category: [] for category in CATEGORIES.keys()}
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1].lower()
                categorized = False
                for category, extensions in CATEGORIES.items():
                    if file_extension in extensions:
                        categorized = True
                        category_folder = os.path.join(directory, category)
                        if not os.path.exists(category_folder):
                            os.makedirs(category_folder)
                        new_path = os.path.join(category_folder, file)
                        if file_path != new_path:
                            os.rename(file_path, new_path)
                        organized_files[category].append(new_path)
                        break
                if not categorized:  # Uncategorized files
                    others_folder = os.path.join(directory, "Others")
                    if not os.path.exists(others_folder):
                        os.makedirs(others_folder)
                    new_path = os.path.join(others_folder, file)
                    if file_path != new_path:
                        os.rename(file_path, new_path)
                    organized_files["Others"].append(new_path)
        return organized_files
    def update_tab_content(self, tab_frame, organized_files):
        """Updates the content of a tab with organized files."""
        for widget in tab_frame.winfo_children():
            widget.destroy()
        for category, files in organized_files.items():
            if files:
                tk.Label(tab_frame, text=f"{category}:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
                frame = ttk.Frame(tab_frame)
                frame.pack(fill="both", padx=10, pady=5, expand=True)
                text_area = tk.Text(frame, wrap="word", height=10)
                scrollbar = ttk.Scrollbar(frame, command=text_area.yview)
                text_area.configure(yscrollcommand=scrollbar.set)
                text_area.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                for file in files:
                    filename = os.path.basename(file)
                    text_area.insert("end", f"{filename} ({os.path.splitext(file)[1]})\n")
                    text_area.tag_add("file_link", f"{text_area.index('end')}-2l", f"{text_area.index('end')}-1c")
                    text_area.tag_config("file_link", foreground="blue", underline=True)
                    text_area.tag_bind("file_link", "<Button-1>", lambda e, path=file: self.open_file(path))
                text_area.config(state="disabled")
    def open_file(self, file_path):
        """Opens a file or folder."""
        try:
            os.startfile(file_path)  # For Windows
        except Exception as e:
            messagebox.showerror("Error", f"Could not open {file_path}: {e}")
# Main Program
if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()