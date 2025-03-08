import tkinter as tk
from tkinter import ttk, messagebox
import yt_dlp
from pathlib import Path
import threading
import time

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Videos")
        self.root.geometry("700x500")
        
        # Crear el directorio de descargas
        self.download_path = Path("./downloads")
        self.download_path.mkdir(exist_ok=True)
        
        # Variables para el progreso
        self.download_speed = 0
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.eta = 0
        self.current_format = None
        
        # Crear widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL input
        ttk.Label(main_frame, text="URL del video:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Botón para obtener formatos disponibles
        self.format_button = ttk.Button(main_frame, text="Obtener Formatos", command=self.get_formats)
        self.format_button.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Selector de formato
        ttk.Label(main_frame, text="Formato:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(main_frame, textvariable=self.format_var, state='disabled')
        self.format_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=300, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Botón de descarga
        self.download_button = ttk.Button(main_frame, text="Descargar", command=self.start_download)
        self.download_button.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Estado
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Información de descarga
        self.info_frame = ttk.LabelFrame(main_frame, text="Información de descarga", padding="5")
        self.info_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.speed_label = ttk.Label(self.info_frame, text="Velocidad: -")
        self.speed_label.grid(row=0, column=0, sticky=tk.W)
        
        self.eta_label = ttk.Label(self.info_frame, text="Tiempo restante: -")
        self.eta_label.grid(row=1, column=0, sticky=tk.W)
        
        self.size_label = ttk.Label(self.info_frame, text="Tamaño: -")
        self.size_label.grid(row=2, column=0, sticky=tk.W)

    def get_formats(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor ingresa una URL")
            return
        
        self.format_button.state(['disabled'])
        self.status_label.config(text="Obteniendo formatos disponibles...")
        
        thread = threading.Thread(target=self._fetch_formats, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _fetch_formats(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = []
                for f in info['formats']:
                    # Solo incluir formatos con video
                    if f.get('vcodec') != 'none':
                        format_note = f.get('format_note', '')
                        ext = f.get('ext', '')
                        resolution = f.get('resolution', '')
                        format_id = f['format_id']
                        formats.append(f"{resolution} - {format_note} ({ext}) [{format_id}]")
                
                self.root.after(0, self._update_formats, formats)
        except Exception as e:
            self.root.after(0, self._show_format_error, str(e))
    
    def _update_formats(self, formats):
        self.format_combo['values'] = formats
        self.format_combo['state'] = 'readonly'
        self.format_button.state(['!disabled'])
        self.status_label.config(text="Formatos cargados. Selecciona uno para descargar.")
        if formats:
            self.format_combo.set(formats[0])
    
    def _show_format_error(self, error):
        self.format_button.state(['!disabled'])
        self.status_label.config(text=f"Error: {error}")
        messagebox.showerror("Error", f"Error al obtener formatos: {error}")
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            self.download_speed = d.get('speed', 0)
            self.downloaded_bytes = d.get('downloaded_bytes', 0)
            self.total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            self.eta = d.get('eta', 0)
            
            # Actualizar la interfaz
            self.root.after(0, self._update_progress)
    
    def _update_progress(self):
        if self.total_bytes > 0:
            progress = (self.downloaded_bytes / self.total_bytes) * 100
            self.progress_var.set(progress)
            
            # Actualizar etiquetas de información
            speed_str = f"Velocidad: {self._format_speed(self.download_speed)}"
            eta_str = f"Tiempo restante: {self._format_eta(self.eta)}"
            size_str = f"Tamaño: {self._format_bytes(self.downloaded_bytes)}/{self._format_bytes(self.total_bytes)}"
            
            self.speed_label.config(text=speed_str)
            self.eta_label.config(text=eta_str)
            self.size_label.config(text=size_str)
    
    def _format_speed(self, speed):
        if speed is None or speed == 0:
            return "- B/s"
        if speed < 1024:
            return f"{speed:.1f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed/1024:.1f} KB/s"
        else:
            return f"{speed/(1024*1024):.1f} MB/s"
    
    def _format_eta(self, eta):
        if eta is None or eta == 0:
            return "-"
        minutes, seconds = divmod(eta, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"
    
    def _format_bytes(self, bytes):
        if bytes is None or bytes == 0:
            return "0 B"
        if bytes < 1024:
            return f"{bytes} B"
        elif bytes < 1024 * 1024:
            return f"{bytes/1024:.1f} KB"
        elif bytes < 1024 * 1024 * 1024:
            return f"{bytes/(1024*1024):.1f} MB"
        else:
            return f"{bytes/(1024*1024*1024):.1f} GB"
            
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor ingresa una URL")
            return
            
        if not self.format_var.get():
            messagebox.showerror("Error", "Por favor selecciona un formato")
            return
        
        # Obtener el format_id del formato seleccionado
        format_id = self.format_var.get().split('[')[-1].strip(']')
        
        self.download_button.state(['disabled'])
        self.format_button.state(['disabled'])
        self.format_combo.state(['disabled'])
        self.status_label.config(text="Descargando...")
        self.progress_var.set(0)
        
        # Reiniciar variables de progreso
        self.download_speed = 0
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.eta = 0
        
        # Iniciar descarga en un hilo separado
        thread = threading.Thread(target=self.download_video, args=(url, format_id))
        thread.daemon = True
        thread.start()
        
    def download_video(self, url, format_id):
        try:
            ydl_opts = {
                'format': format_id,
                'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'no_warnings': True,
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                self.root.after(0, self.download_complete, "¡Descarga completada!", video_path)
        except Exception as e:
            self.root.after(0, self.download_error, f"Error: {str(e)}")
            
    def download_complete(self, message, path):
        self.download_button.state(['!disabled'])
        self.format_button.state(['!disabled'])
        self.format_combo.state(['readonly'])
        self.status_label.config(text=message)
        messagebox.showinfo("Éxito", f"Video descargado en:\n{path}")
        
    def download_error(self, message):
        self.download_button.state(['!disabled'])
        self.format_button.state(['!disabled'])
        self.format_combo.state(['readonly'])
        self.status_label.config(text=message)
        messagebox.showerror("Error", message)

def main():
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
