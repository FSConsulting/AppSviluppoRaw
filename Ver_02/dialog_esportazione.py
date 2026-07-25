"""Dialog per l'esportazione singola di immagini sviluppate.

Implementa `DialogEsportazione`, una finestra modale che permette di
selezionare il profilo di esportazione (Web/Social/Stampa) e salvare la
versione risultante su disco. La finestra gestisce UI e feedback verso
l'utente durante l'operazione.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from esportatore_canali import EsportatoreCanali

class DialogEsportazione(tk.Toplevel):
    """Finestra di dialogo popup per configurare ed eseguire l'esportazione di una singola foto RAW."""
    
    def __init__(self, parent, file_raw, parametri):
        super().__init__(parent)
        self.file_raw = file_raw
        self.parametri = parametri
        
        self.title("Esportazione Singola Immagine")
        self.geometry("450x250")
        self.resizable(False, False)
        self.grab_set()  # Rende la finestra modale
        
        self.profilo_selezionato = tk.StringVar(value="Web")
        self.crea_interfaccia()
        self.center_window(parent)
        
    def center_window(self, parent):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def crea_interfaccia(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Info file
        nome_file = os.path.basename(self.file_raw)
        ttk.Label(frame, text=f"File sorgente: {nome_file}", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 15))
        
        # Selezione Canale/Profilo
        ttk.Label(frame, text="Seleziona il profilo di esportazione destinazione:").pack(anchor=tk.W, pady=(0, 5))
        
        canali = [
            ("Web (Ottimizzato sRGB, lato lungo 1920px)", "Web"),
            ("Social (Instagram/Facebook, lato lungo 1080px)", "Social"),
            ("Stampa High-Res (Risoluzione nativa massima)", "Stampa")
        ]
        
        for testo, valore in canali:
            ttk.Radiobutton(frame, text=testo, value=valore, variable=self.profilo_selezionato).pack(anchor=tk.W, pady=2)
            
        # Bottoni Azione
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="💾 Esporta", command=self.esegui_esportazione).pack(side=tk.RIGHT, padx=5)

    def esegui_esportazione(self):
        """Esegue il salvataggio dell'immagine secondo il profilo selezionato.

        Mostra finestre di dialogo per il salvataggio e utilizza
        :class:`esportatore_canali.EsportatoreCanali` per la scrittura su disco.
        """
        estensione_dest = ".jpg"
        if self.profilo_selezionato.get() == "Stampa":
            estensione_dest = ".tiff"
            file_types = [("TIFF Immagine", "*.tiff"), ("JPEG Immagine", "*.jpg")]
        else:
            file_types = [("JPEG Immagine", "*.jpg")]
            
        nome_default = os.path.splitext(os.path.basename(self.file_raw))[0] + estensione_dest
        
        file_salvataggio = filedialog.asksaveasfilename(
            parent=self,
            title="Salva immagine esportata",
            initialfile=nome_default,
            filetypes=file_types
        )
        
        if not file_salvataggio:
            return
            
        self.configura_cursore_attesa(True)
        try:
            successo = EsportatoreCanali.esporta_singolo(
                self.file_raw, 
                file_salvataggio, 
                self.parametri, 
                self.profilo_selezionato.get()
            )
            if successo:
                messagebox.showinfo("Successo", "Esportazione completata con successo!", parent=self)
                self.destroy()
            else:
                messagebox.showerror("Errore", "Impossibile completare l'esportazione.", parent=self)
        except Exception as e:
            messagebox.showerror("Errore di Sistema", f"Errore critico durante l'elaborazione:\n{str(e)}", parent=self)
        finally:
            self.configura_cursore_attesa(False)

    def configura_cursore_attesa(self, attesa: bool):
        cursore = "watch" if attesa else ""
        self.config(cursor=cursore)
        self.update()
