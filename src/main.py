from threading import Thread
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from internal_google_apis import GDriveAgent
import hurry.filesize 

class MainWindow(tk.Tk):
    def __init__(self):
        self.gdrive_agent = GDriveAgent()
        self.set_file_data()
        super().__init__()
        self.geometry("640x480")
        self.title("Read-only File Downloader")
        self.create_prompt_frame().pack(expand=True)

    def create_prompt_frame(self) -> ttk.Frame:
        self.prompt_frame = ttk.Frame(self)
        self.prompt_var = tk.StringVar()
        self.prompt_var.set("Enter File ID")
        self.prompt_label = ttk.Label(self.prompt_frame, textvariable=self.prompt_var)
        self.prompt_label.pack()
        self.link = tk.StringVar()
        self.link_field = tk.Entry(self.prompt_frame, textvariable=self.link, font=('calibre',10,'normal'))
        self.link_field.pack()
        self.verify_button = ttk.Button(self.prompt_frame, text="Verify File", command=self.on_verify_button_clicked)
        self.verify_button.pack()

        return self.prompt_frame

    def on_verify_button_clicked(self):
        drive_file_identifier = self.link.get()
        self.verify_by_id(drive_file_identifier)

    def verify_by_id(self, id):
        file_metadata = self.gdrive_agent.get_file_metadata(id)
        try:
            if file_metadata['kind'] == 'drive#file':
                file_name = file_metadata['title']
                file_size = int(file_metadata['fileSize'])
                self.set_file_data(file_name, file_size, id)
                self.prompt_frame.destroy()
                self.create_download_frame().pack(expand=True)
            else:
                self.prompt_var.set("Invalid File! Enter File ID")
        except:
            self.prompt_var.set("Invalid File! Enter File ID")

    def set_file_data(self, name="", size=0, id=""):
        self.cancel_download = False
        self.file_name = name
        self.file_size = size
        self.file_id = id

    def create_download_frame(self) -> ttk.Frame:
        self.download_frame = ttk.Frame(self)
        self.file_name_label = ttk.Label(self.download_frame, text=self.file_name)
        self.download_button = ttk.Button(self.download_frame, text="Download", command=self.on_download_button_clicked)
        self.file_size_label = ttk.Label(self.download_frame, text=hurry.filesize.size(self.file_size))
        self.go_back_button = ttk.Button(self.download_frame, text="Cancel", command=self.go_back_from_download)
        self.file_name_label.pack()
        self.download_button.pack()
        self.file_size_label.pack()
        self.go_back_button.pack()
        return self.download_frame

    def on_download_button_clicked(self):
        self.download_frame.destroy()
        self.new_thread = Thread(target=self.download, daemon=True)
        self.new_thread.start()
    

    def go_back_from_download(self):
        self.set_file_data("", "", "")
        self.download_frame.destroy()
        self.create_prompt_frame().pack(expand=True)

    def create_progress_frame(self) -> ttk.Frame:
        self.progress_frame = ttk.Frame(self)
        self.progress_percent = tk.IntVar()
        self.progress_percent.set(0)
        self.download_progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_percent)
        self.cancel_button = ttk.Button(self.progress_frame, text="Cancel", command=self.on_cancel_button_clicked)
        self.download_status = tk.StringVar()
        self.download_status.set("Downloading..")
        self.download_label = ttk.Label(self.progress_frame, textvariable=self.download_status)
        self.download_label.pack()
        self.download_progress_bar.pack()
        self.cancel_button.pack()

        return self.progress_frame

    def on_cancel_button_clicked(self):
        self.progress_frame.destroy()
        self.cancel_download = True
        self.create_download_frame().pack(expand=True)

    def download(self):
        self.create_progress_frame().pack(expand=True)
        self.cancel_download = False
        progress_gen = self.gdrive_agent.get_file(self.file_id, self.file_name)
        while not self.cancel_download:
            try:
                progress = next(progress_gen)
                self.download_status.set(str("Downloading " + str(int((100*progress)/self.file_size)) + "%"))
                self.progress_percent.set((100*progress)/self.file_size)
            except StopIteration:
                break
        if self.cancel_download:
            return
        self.start_over_button = tk.Button(self.progress_frame, text="Download Another File", command=self.start_over)
        self.start_over_button.pack()
        self.cancel_button.destroy()

    
    def start_over(self):
        self.set_file_data()
        self.progress_frame.destroy()
        self.create_prompt_frame().pack(expand=True)



if __name__ == "__main__":
    main_window = MainWindow()
    main_window.mainloop()