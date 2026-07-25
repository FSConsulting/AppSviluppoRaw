# 📷 Nikon NEF Batch Editor - Report Avanzamento Progetto

Questo file contiene lo stato attuale dell'architettura software divisa in moduli compatti.

## 🗂️ Struttura dei File del Progetto

* **`requirements.txt`**: Dipendenze del progetto
* **`app_gui.py`**: Interfaccia grafica principale e coordinamento
* **`componenti_gui.py`**: Struttura visiva, widget e slider laterali
* **`collezione_manager.py`**: Gestione dello stato della lista file RAW
* **`interazione_manager.py`**: Logica del mouse, drag e zoom sul canvas
* **`ritocco_manager.py`**: Strumento pennello e coordinate rimozione macchie
* **`database_manager.py`**: Persistenza SQLite e migrazione dei dati
* **`motore_sviluppo.py`**: Sviluppo RAW, filtri PIL e rimozione macchie
* **`esportatore_canali.py`**: Logica di ricampionamento Stampa, Social, Web e Batch
* **`dialog_esportazione.py`**: Finestra di dialogo popup per il salvataggio singolo

---

## 📄 File: `requirements.txt`
**Descrizione**: Dipendenze del progetto

```txt
rawpy>=0.21.0
Pillow>=10.0.0
numpy>=1.24.0
```

---

## 📄 File: `app_gui.py`
**Descrizione**: Interfaccia grafica principale e coordinamento

```python
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from motore_sviluppo import MotoreSviluppo
from componenti_gui import ComponentiGui
from collezione_manager import CollezioneManager
from interazione_manager import InterazioneManager
from ritocco_manager import RitoccoManager

class AppSviluppoRaw:
    """Interfaccia principale con adattamento corretto dell'anteprima e reset degli slider."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Nikon NEF Batch Editor")
        self.root.geometry("1200x800")
        
        self.collezione = CollezioneManager()
        self.interazione = InterazioneManager(self)
        self.ritocco = RitoccoManager(self)
        
        self.img_anteprima_base = self.tk_foto = None
        self.in_zoom = False
        self.w_visualizzato = self.h_visualizzato = 1
        self.x_offset_canvas = self.y_offset_canvas = 0
        
        ComponentiGui.crea_layout(self)
        ComponentiGui.crea_controlli(self)
        self.configura_bindings()
        self.root.protocol("WM_DELETE_WINDOW", self.gestisci_chiusura_app)
        
    def configura_bindings(self):
        self.canvas_foto.bind("<Double-Button-1>", self.interazione.gestisci_doppio_click)
        self.root.bind("<Escape>", self.interazione.annulla_zoom)
        self.canvas_foto.bind("<Button-1>", self.interazione.inizia_trascinamento)
        self.canvas_foto.bind("<B1-Motion>", self.interazione.esegui_trascinamento)
        self.root.bind("<Right>", lambda e: self.foto_successiva())
        self.root.bind("<Left>", lambda e: self.foto_precedente())

    def attiva_strumento_macchie(self):
        self.ritocco.switch_stato()
        testo = "🧹 Disattiva Pennello Macchie" if self.ritocco.attivo else "🧹 Attiva Pennello Macchie"
        self.btn_macchie.config(text=testo)

    def raccogli_parametri_attuali(self) -> dict:
        return {
            'brightness': self.sld_brightness.get(), 'contrast': self.sld_contrast.get(),
            'saturation': self.sld_saturation.get(), 'sharpness': self.sld_sharpness.get(),
            'denoise': self.sld_denoise.get(), 'rotation': self.sld_rotation.get(),
            'distortion': self.sld_distortion.get(), 'crop': self.sld_crop.get(),
            'margine': self.sld_margine.get(), 'is_bw': self.var_bw.get(),
            'esportare': self.var_esportare.get(), 'macchie': self.ritocco.macchie
        }

    def applica_parametri_a_gui(self, par: dict):
        self.blocco_salvataggio = True
        self.sld_brightness.set(par.get('brightness', 1.00))
        self.sld_contrast.set(par.get('contrast', 1.10))
        self.sld_saturation.set(par.get('saturation', 1.05))
        self.sld_sharpness.set(par.get('sharpness', 150))
        self.sld_denoise.set(par.get('denoise', 0.0))
        self.sld_rotation.set(par.get('rotation', 0.0))
        self.sld_distortion.set(par.get('distortion', 0.0))
        self.sld_crop.set(par.get('crop', 0.0))
        self.sld_margine.set(par.get('margine', 0.0))
        self.var_bw.set(par.get('is_bw', False))
        self.var_esportare.set(par.get('esportare', False))
        self.ritocco.macchie = par.get('macchie', [])
        self.blocco_salvataggio = False

    def salva_stato_corrente(self):
        if hasattr(self, 'blocco_salvataggio') and self.blocco_salvataggio: return
        if self.collezione.file_attivo and self.collezione.db_manager:
            self.collezione.db_manager.salva_parametri(self.collezione.file_attivo, self.raccogli_parametri_attuali())

    def gestisci_modalita_colore(self):
        if self.collezione.file_attivo:
            self.salva_stato_corrente()
            self.root.config(cursor="watch"); self.root.update()
            try:
                self.img_anteprima_base = MotoreSviluppo.estrai_immagine_nativa(self.collezione.file_attivo, forza_colore=not self.var_bw.get())
                self.aggiorna_anteprima()
            except Exception as e: messagebox.showerror("Errore", str(e))
            finally: self.root.config(cursor="")

    def carica_cartella_raw(self):
        cartella = filedialog.askdirectory()
        if cartella and self.collezione.inizializza_cartella(cartella):
            self.btn_prev.config(state=tk.NORMAL)
            self.btn_next.config(state=tk.NORMAL)
            self.carica_immagine_da_stato()

    def carica_immagine_da_stato(self):
        if self.collezione.file_attivo:
            self.ritocco.disattiva()
            self.btn_macchie.config(text="🧹 Attiva Pennello Macchie")
            self.canvas_foto.delete("all")
            self.tk_foto = self.img_anteprima_base = None
            self.in_zoom = False
            self.lbl_info_file.config(text=self.collezione.ottieni_testo_info(), foreground="black")
            par = self.collezione.db_manager.carica_parametri(self.collezione.file_attivo)
            self.applica_parametri_a_gui(par) if par else self.applica_parametri_a_gui({})
            self.root.update_idletasks()
            try:
                self.img_anteprima_base = MotoreSviluppo.estrai_immagine_nativa(self.collezione.file_attivo, forza_colore=not self.var_bw.get())
                self.aggiorna_anteprima()
            except Exception as e: messagebox.showerror("Errore", str(e))

    def foto_successiva(self):
        self.salva_stato_corrente()
        if self.collezione.avanti(): self.carica_immagine_da_stato()

    def foto_precedente(self):
        self.salva_stato_corrente()
        if self.collezione.indietro(): self.carica_immagine_da_stato()

    def aggiorna_anteprima(self, event=None):
        if self.img_anteprima_base is None: return
        self.salva_stato_corrente()
        wc, hc = max(600, self.canvas_foto.winfo_width()), max(500, self.canvas_foto.winfo_height())
        
        img_elaborata = MotoreSviluppo.applica_editing(
            self.img_anteprima_base, self.sld_brightness.get(), self.sld_contrast.get(), 
            self.sld_saturation.get(), self.sld_sharpness.get(), self.sld_denoise.get(),
            self.sld_rotation.get(), self.sld_distortion.get(), self.sld_crop.get(),
            self.sld_margine.get(), self.ritocco.macchie, self.var_bw.get()
        )
        
        # CORRETTO: Creiamo una copia isolata per l'anteprima a schermo per evitare che le proporzioni
        # vengano corrotte o rimpicciolite in modo asimmetrico dopo la rotazione o il crop manuale
        img_anteprima = img_elaborata.copy()
        if not self.in_zoom:
            img_anteprima.thumbnail((wc, hc), Image.Resampling.BILINEAR)
            
        self.w_visualizzato, self.h_visualizzato = img_anteprima.width, img_anteprima.height
        iw, ih = max(wc, self.w_visualizzato), max(hc, self.h_visualizzato)
        self.canvas_foto.config(scrollregion=(0, 0, iw, ih))
        self.x_offset_canvas, self.y_offset_canvas = (iw - self.w_visualizzato) // 2, (ih - self.h_visualizzato) // 2
        
        self.tk_foto = ImageTk.PhotoImage(img_anteprima)
        self.canvas_foto.delete("all")
        self.canvas_foto.create_image(iw // 2, ih // 2, image=self.tk_foto, anchor=tk.CENTER)

    def esegui_batch_completo(self):
        from esportatore_canali import EsportatoreCanali
        if not self.collezione.db_manager: return
        self.salva_stato_corrente()
        coda = self.collezione.db_manager.ottieni_coda_esportazione()
        if not coda: return
        cartella_lavoro = os.path.dirname(self.collezione.file_attivo)
        self.root.config(cursor="watch")
        try:
            EsportatoreCanali.esegui_esportazione_batch(cartella_lavoro, coda, callback_progresso=lambda c, t, f: (self.lbl_progresso_batch.config(text=f"Sviluppo: {c}/{t}", foreground="orange"), self.root.update()))
            self.lbl_progresso_batch.config(text="Stato: Batch Completato!", foreground="darkgreen")
        except Exception as e: messagebox.showerror("Errore", str(e))
        finally: self.root.config(cursor="")

    def apri_dialog_esportazione_singola(self):
        from dialog_esportazione import DialogEsportazioneSingola
        DialogEsportazioneSingola.apri(self)

    def gestisci_chiusura_app(self):
        self.salva_stato_corrente()
        self.root.destroy()

if __name__ == "__main__":
    window = tk.Tk()
    app = AppSviluppoRaw(window)
    window.mainloop()
```

---

## 📄 File: `componenti_gui.py`
**Descrizione**: Struttura visiva, widget e slider laterali

```python
import tkinter as tk
from tkinter import ttk

class ComponentiGui:
    """Classe statica responsabile del layout e del binding del doppio clic di reset sugli slider."""

    @staticmethod
    def crea_layout(app):
        app.style = ttk.Style()
        app.style.theme_use("clam")
        app.pan_sinistro = ttk.Frame(app.root, padding=10, width=320)
        app.pan_sinistro.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        app.pan_sinistro.pack_propagate(False)
        app.pan_destro = ttk.Frame(app.root, padding=10)
        app.pan_destro.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    @staticmethod
    def crea_controlli(app):
        # Sezione Cartelle
        ttk.Label(app.pan_sinistro, text="🗂️ CARTELLE", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
        ttk.Button(app.pan_sinistro, text="Apri Cartella RAW", command=app.carica_cartella_raw).pack(fill=tk.X, pady=2)
        app.lbl_info_file = ttk.Label(app.pan_sinistro, text="Nessuna cartella", wraplength=280, foreground="gray")
        app.lbl_info_file.pack(anchor=tk.W, pady=5)
        
        app.pan_navigazione = ttk.Frame(app.pan_sinistro)
        app.pan_navigazione.pack(fill=tk.X, pady=5)
        app.btn_prev = ttk.Button(app.pan_navigazione, text="⬅️ Prec", command=app.foto_precedente, state=tk.DISABLED, takefocus=False)
        app.btn_prev.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        app.btn_next = ttk.Button(app.pan_navigazione, text="Succ ➡️", command=app.foto_successiva, state=tk.DISABLED, takefocus=False)
        app.btn_next.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        ttk.Separator(app.pan_sinistro).pack(fill=tk.X, pady=5)
        
        # Sezione Sviluppo Base
        ttk.Label(app.pan_sinistro, text="🎛️ SVILUPPO BASE", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
        app.var_bw = tk.BooleanVar(value=False)
        ttk.Checkbutton(app.pan_sinistro, text="Forza Bianco e Nero (B&W)", variable=app.var_bw, command=app.gestisci_modalita_colore).pack(anchor=tk.W, pady=2)
        app.var_esportare = tk.BooleanVar(value=False)
        ttk.Checkbutton(app.pan_sinistro, text="🎯 Includi in Esportazione Batch", variable=app.var_esportare, command=app.salva_stato_corrente).pack(anchor=tk.W, pady=2)
        
        # Definizione slider base con passati i loro valori di default di fabbrica
        app.sld_brightness = ComponentiGui._slider(app.pan_sinistro, "Luminosità", 0.5, 1.8, 1.00, 1.00, app)
        app.sld_contrast = ComponentiGui._slider(app.pan_sinistro, "Contrasto", 0.5, 1.8, 1.10, 1.10, app)
        app.sld_saturation = ComponentiGui._slider(app.pan_sinistro, "Vividezza", 0.5, 2.0, 1.05, 1.05, app)
        app.sld_sharpness = ComponentiGui._slider(app.pan_sinistro, "Nitidezza", 0, 250, 150, 150, app)
        
        ttk.Separator(app.pan_sinistro).pack(fill=tk.X, pady=5)
        
        # Sezione Correzioni e Inquadratura
        ttk.Label(app.pan_sinistro, text="⚙️ CORREZIONI E RITAGLIO", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
        app.sld_denoise = ComponentiGui._slider(app.pan_sinistro, "Riduzione Rumore", 0.0, 4.0, 0.0, 0.0, app)
        app.sld_rotation = ComponentiGui._slider(app.pan_sinistro, "Orizzonte (Rotazione fine)", -10.0, 10.0, 0.0, 0.0, app)
        app.sld_distortion = ComponentiGui._slider(app.pan_sinistro, "Deformazione Lente", -0.5, 0.5, 0.0, 0.0, app)
        app.sld_crop = ComponentiGui._slider(app.pan_sinistro, "Riquadratura (Crop %)", 0.0, 40.0, 0.0, 0.0, app)
        app.sld_margine = ComponentiGui._slider(app.pan_sinistro, "Margine di Ritaglio bordi %", 0.0, 20.0, 0.0, 0.0, app)
        
        app.btn_macchie = ttk.Button(app.pan_sinistro, text="🧹 Attiva Pennello Macchie", command=app.attiva_strumento_macchie)
        app.btn_macchie.pack(fill=tk.X, pady=4)
        
        ttk.Separator(app.pan_sinistro).pack(fill=tk.X, pady=5)
        
        # Sezione Esportazione
        ttk.Label(app.pan_sinistro, text="💾 ESPORTAZIONE AUTOMATICA", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
        ttk.Button(app.pan_sinistro, text="💾 Salva Foto Corrente...", command=app.apri_dialog_esportazione_singola).pack(fill=tk.X, pady=2)
        ttk.Button(app.pan_sinistro, text="🚀 AVVIA BATCH SULLE SELEZIONATE", command=app.esegui_batch_completo).pack(fill=tk.X, pady=2)
        
        app.lbl_progresso_batch = ttk.Label(app.pan_sinistro, text="Stato: Pronto", foreground="darkgreen", font=("Arial", 9, "italic"))
        app.lbl_progresso_batch.pack(anchor=tk.W, pady=2)
        app.canvas_foto = tk.Canvas(app.pan_destro, bg="#2b2b2b")
        app.canvas_foto.pack(fill=tk.BOTH, expand=True)

    @staticmethod
    def _slider(parent, testo, da, a, val, default_val, app):
        """Genera lo slider aggiungendo l'evento Double-Click per resettare al valore originale."""
        ttk.Label(parent, text=testo).pack(anchor=tk.W, pady=0)
        s = ttk.Scale(parent, from_=da, to=a, value=val, command=lambda v: app.aggiorna_anteprima())
        s.pack(fill=tk.X, pady=0)
        
        # Binding del doppio click sul singolo widget per resettare al valore nativo originale
        s.bind("<Double-Button-1>", lambda event, widget=s, dv=default_val: (widget.set(dv), app.aggiorna_anteprima()))
        return s
```

---

## 📄 File: `collezione_manager.py`
**Descrizione**: Gestione dello stato della lista file RAW

```python
import os
from database_manager import DatabaseManager

class CollezioneManager:
    """Classe responsabile della gestione dello stato della lista file e dell'indice corrente."""
    
    def __init__(self):
        self.lista_files = []
        self.indice_corrente = -1
        self.file_attivo = None
        self.db_manager = None

    def inizializza_cartella(self, cartella: str) -> bool:
        """Carica i file .nef della cartella e sincronizza il database."""
        file_trovati = {
            os.path.join(cartella, f) 
            for f in os.listdir(cartella) 
            if f.lower().endswith('.nef')
        }
        self.lista_files = sorted(list(file_trovati))
        
        if not self.lista_files:
            return False
            
        self.db_manager = DatabaseManager(cartella)
        self.db_manager.sincronizza_file_cartella(self.lista_files)
        self.indice_corrente = self.db_manager.trova_indice_prima_foto_vergine(self.lista_files)
        self.aggiorna_file_attivo()
        return True

    def aggiorna_file_attivo(self):
        """Aggiorna il puntatore al file attivo in base all'indice."""
        if 0 <= self.indice_corrente < len(self.lista_files):
            self.file_attivo = self.lista_files[self.indice_corrente]
        else:
            self.file_attivo = None

    def avanti(self) -> bool:
        """Sposta l'indice in avanti se possibile."""
        if self.indice_corrente < len(self.lista_files) - 1:
            self.indice_corrente += 1
            self.aggiorna_file_attivo()
            return True
        return False

    def indietro(self) -> bool:
        """Sposta l'indice all'indietro se possibile."""
        if self.indice_corrente > 0:
            self.indice_corrente -= 1
            self.aggiorna_file_attivo()
            return True
        return False

    def ottieni_testo_info(self) -> str:
        """Ritorna la stringa di info per la label della GUI."""
        if not self.file_attivo:
            return "Nessuna cartella"
        nome = os.path.basename(self.file_attivo)
        return f"Foto [{self.indice_corrente + 1}/{len(self.lista_files)}]\nFile: {nome}"
```

---

## 📄 File: `interazione_manager.py`
**Descrizione**: Logica del mouse, drag e zoom sul canvas

```python
import tkinter as tk
from calcolatore_gui import CalcolatoreGui
from motore_sviluppo import MotoreSviluppo

class InterazioneManager:
    """Isola tutta la logica del mouse, dello zoom tridimensionale e del trascinamento sul canvas."""
    
    def __init__(self, app):
        self.app = app

    def gestisci_doppio_click(self, event):
        if self.app.img_anteprima_base is None: 
            return
        if self.app.in_zoom: 
            self.annulla_zoom()
            return
        
        cx = self.app.canvas_foto.canvasx(event.x) - self.app.x_offset_canvas
        cy = self.app.canvas_foto.canvasy(event.y) - self.app.y_offset_canvas
        
        if 0 <= cx <= self.app.w_visualizzato and 0 <= cy <= self.app.h_visualizzato:
            px, py = cx / self.app.w_visualizzato, cy / self.app.h_visualizzato
            self.app.in_zoom = True
            self.app.aggiorna_anteprima()
            self.app.root.update_idletasks()
            
            tx, ty = CalcolatoreGui.calcola_centratura_zoom(
                px, py, self.app.w_visualizzato, self.app.h_visualizzato, 
                self.app.x_offset_canvas, self.app.y_offset_canvas, 
                self.app.canvas_foto.winfo_width(), self.app.canvas_foto.winfo_height()
            )
            self.app.canvas_foto.xview_moveto(tx)
            self.app.canvas_foto.yview_moveto(ty)

    def inizia_trascinamento(self, event):
        if self.app.in_zoom: 
            self.app.canvas_foto.scan_mark(event.x, event.y)

    def esegui_trascinamento(self, event):
        if self.app.in_zoom: 
            self.app.canvas_foto.scan_dragto(event.x, event.y, gain=1)

    def annulla_zoom(self, event=None):
        if self.app.in_zoom:
            self.app.in_zoom = False
            self.app.canvas_foto.xview_moveto(0)
            self.app.canvas_foto.yview_moveto(0)
            self.app.aggiorna_anteprima()
```

---

## 📄 File: `ritocco_manager.py`
**Descrizione**: Strumento pennello e coordinate rimozione macchie

```python
import tkinter as tk

class RitoccoManager:
    """Gestisce lo strumento rimozione macchie correggendo il calcolo geometrico in Zoom 100%."""
    
    def __init__(self, app):
        self.app = app
        self.attivo = False
        self.raggio = 15
        self.macchie = []

    def switch_stato(self):
        self.attivo = not self.attivo
        if self.attivo:
            self.app.canvas_foto.config(cursor="none")
            self.app.canvas_foto.bind("<Motion>", self.disegna_pennello)
            self.app.canvas_foto.bind("<MouseWheel>", self.regola_raggio)
            self.app.canvas_foto.bind("<Button-1>", self.registra_macchia)
        else:
            self.disattiva()

    def disattiva(self):
        self.attivo = False
        self.app.canvas_foto.config(cursor="")
        self.app.canvas_foto.delete("pennello_ritocco")
        self.app.canvas_foto.unbind("<Motion>")
        self.app.canvas_foto.unbind("<MouseWheel>")
        self.app.canvas_foto.bind("<Button-1>", self.app.interazione.inizia_trascinamento)

    def disegna_pennello(self, event):
        # Rileva la coordinata tenendo conto dello scroll sul canvas virtuale
        ax = self.app.canvas_foto.canvasx(event.x)
        ay = self.app.canvas_foto.canvasy(event.y)
        self.app.canvas_foto.delete("pennello_ritocco")
        self.app.canvas_foto.create_oval(
            ax - self.raggio, ay - self.raggio,
            ax + self.raggio, ay + self.raggio,
            outline="red", width=2, tags="pennello_ritocco"
        )

    def regola_raggio(self, event):
        if event.delta > 0:
            self.raggio = min(80, self.raggio + 2)
        else:
            self.raggio = max(5, self.raggio - 2)
        self.disegna_pennello(event)

    def registra_macchia(self, event):
        if self.app.img_anteprima_base is None:
            return
            
        # Determina la posizione sul canvas virtuale comprensiva di scorrimento
        ax = self.app.canvas_foto.canvasx(event.x)
        ay = self.app.canvas_foto.canvasy(event.y)
        
        # CORRETTO: In modalità zoom escludiamo gli offset per prevenire lo spostamento in basso a sinistra
        if self.app.in_zoom:
            cx = ax
            cy = ay
        else:
            cx = ax - self.app.x_offset_canvas
            cy = ay - self.app.y_offset_canvas
        
        if 0 <= cx <= self.app.w_visualizzato and 0 <= cy <= self.app.h_visualizzato:
            # Calcolo del fattore di scala reale rispetto alla matrice nativa originale
            scala_x = self.app.img_anteprima_base.width / self.app.w_visualizzato
            scala_y = self.app.img_anteprima_base.height / self.app.h_visualizzato
            
            rx = int(cx * scala_x)
            ry = int(cy * scala_y)
            rr = int(self.raggio * scala_x)
            
            self.macchie.append((rx, ry, rr))
            
            # Sincronizzazione immediata sul Database e re-rendering
            self.app.salva_stato_corrente()
            self.app.aggiorna_anteprima()
            self.app.root.update_idletasks()
            self.disegna_pennello(event)
```

---

## 📄 File: `database_manager.py`
**Descrizione**: Persistenza SQLite e migrazione dei dati

```python
import os
import sqlite3
import re
from typing import Optional, Dict, Any, List, Tuple

class DatabaseManager:
    """Classe responsabile della persistenza dello stato e della migrazione sicura dei dati."""

    def __init__(self, cartella_path: str):
        self.db_path = os.path.join(cartella_path, "workflow_raw.db")
        self._inizializza_db()
        self._esegui_migrazioni()
        self._sanifica_dati_macchie()

    def _inizializza_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS modifiche (
                    file_name TEXT PRIMARY KEY,
                    brightness REAL DEFAULT 1.0,
                    contrast REAL DEFAULT 1.1,
                    saturation REAL DEFAULT 1.05,
                    sharpness REAL DEFAULT 150.0,
                    denoise REAL DEFAULT 0.0,
                    rotation REAL DEFAULT 0.0,
                    distortion REAL DEFAULT 0.0,
                    crop REAL DEFAULT 0.0,
                    margine REAL DEFAULT 0.0,
                    is_bw INTEGER DEFAULT 0,
                    esportare INTEGER DEFAULT 0,
                    macchie TEXT DEFAULT '',
                    modificato INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def _esegui_migrazioni(self):
        """Controlla l'esistenza effettiva dei nomi delle colonne prima di eseguire l'ALTER TABLE."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(modifiche)")
            # CORRETTO: Estraiamo row[1] che rappresenta il nome testuale della colonna (es. 'crop')
            nomi_colonne = {row[1] for row in cursor.fetchall()}
            
            if "crop" not in nomi_colonne:
                cursor.execute("ALTER TABLE modifiche ADD COLUMN crop REAL DEFAULT 0.0")
            if "margine" not in nomi_colonne:
                cursor.execute("ALTER TABLE modifiche ADD COLUMN margine REAL DEFAULT 0.0")
            # RISOLTO IL BUG: Cambiato da 'colonne' a 'nomi_colonne'
            if "esportare" not in nomi_colonne:
                cursor.execute("ALTER TABLE modifiche ADD COLUMN esportare INTEGER DEFAULT 0")
            if "macchie" not in nomi_colonne:
                cursor.execute("ALTER TABLE modifiche ADD COLUMN macchie TEXT DEFAULT ''")
            conn.commit()

    def _sanifica_dati_macchie(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_name, macchie FROM modifiche WHERE macchie IS NOT NULL AND macchie != ''")
            records = cursor.fetchall()
            
            for file_name, vecchia_str in records:
                if not vecchia_str: continue
                numeri = re.findall(r'\d+', vecchia_str)
                if len(numeri) == 0 or len(numeri) % 3 != 0:
                    cursor.execute("UPDATE modifiche SET macchie = '' WHERE file_name = ?", (file_name,))
                    continue
                nuove_triplette = []
                for i in range(0, len(numeri), 3):
                    nuove_triplette.append(f"{numeri[i]},{numeri[i+1]},{numeri[i+2]}")
                cursor.execute("UPDATE modifiche SET macchie = ? WHERE file_name = ?", ("|".join(nuove_triplette), file_name))
            conn.commit()

    def sincronizza_file_cartella(self, lista_file_nef: list):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for filepath in lista_file_nef:
                nome_file = os.path.basename(filepath)
                cursor.execute("INSERT OR IGNORE INTO modifiche (file_name) VALUES (?)", (nome_file,))
            conn.commit()

    def salva_parametri(self, filepath: str, parametri: Dict[str, Any]):
        nome_file = os.path.basename(filepath)
        lista_macchie = parametri.get('macchie', [])
        macchie_str = "|".join([f"{m[0]},{m[1]},{m[2]}" for m in lista_macchie])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE modifiche 
                SET brightness = ?, contrast = ?, saturation = ?, sharpness = ?, 
                    denoise = ?, rotation = ?, distortion = ?, crop = ?, margine = ?, 
                    is_bw = ?, esportare = ?, macchie = ?, modificato = 1
                WHERE file_name = ?
            """, (
                parametri['brightness'], parametri['contrast'], parametri['saturation'],
                parametri['sharpness'], parametri['denoise'], parametri['rotation'],
                parametri['distortion'], parametri['crop'], parametri['margine'],
                1 if parametri['is_bw'] else 0, 1 if parametri['esportare'] else 0, macchie_str, nome_file
            ))
            conn.commit()

    def carica_parametri(self, filepath: str) -> Optional[Dict[str, Any]]:
        nome_file = os.path.basename(filepath)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM modifiche WHERE file_name = ?", (nome_file,))
            row = cursor.fetchone()
            
            if row and row['modificato'] == 1:
                dati = dict(row)
                m_list = []
                m_str = dati.get('macchie', '')
                if m_str:
                    for item in m_str.split('|'):
                        punti = item.split(',')
                        if len(punti) == 3: m_list.append((int(punti[0]), int(punti[1]), int(punti[2])))
                            
                return {
                    'brightness': dati['brightness'], 'contrast': dati['contrast'],
                    'saturation': dati['saturation'], 'sharpness': dati['sharpness'],
                    'denoise': dati['denoise'], 'rotation': dati['rotation'],
                    'distortion': dati['distortion'], 'crop': dati.get('crop', 0.0),
                    'margine': dati.get('margine', 0.0), 'is_bw': bool(dati['is_bw']),
                    'esportare': bool(dati.get('esportare', 0)), 'macchie': m_list
                }
        return None

    def ottieni_coda_esportazione(self) -> List[Tuple[str, dict]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM modifiche WHERE esportare = 1")
            rows = cursor.fetchall()
            
            coda = []
            for row in rows:
                dati = dict(row)
                m_list = []
                m_str = dati.get('macchie', '')
                if m_str:
                    for item in m_str.split('|'):
                        punti = item.split(',')
                        if len(punti) == 3: m_list.append((int(punti[0]), int(punti[1]), int(punti[2])))
                params = {
                    'brightness': dati['brightness'], 'contrast': dati['contrast'],
                    'saturation': dati['saturation'], 'sharpness': dati['sharpness'],
                    'denoise': dati['denoise'], 'rotation': dati['rotation'],
                    'distortion': dati['distortion'], 'crop': dati.get('crop', 0.0),
                    'margine': dati.get('margine', 0.0), 'is_bw': bool(dati['is_bw']), 'macchie': m_list
                }
                coda.append((dati['file_name'], params))
            return coda

    def trova_indice_prima_foto_vergine(self, lista_file_nef: list) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_name FROM modifiche WHERE modificato = 0")
            file_vergini = {row for row in cursor.fetchall()}
        for index, filepath in enumerate(lista_file_nef):
            if os.path.basename(filepath) in file_vergini: return index
        return 0
```

---

## 📄 File: `motore_sviluppo.py`
**Descrizione**: Sviluppo RAW, filtri PIL e rimozione macchie

```python
import os
import rawpy
import io
import math
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw

class MotoreSviluppo:
    """Core engine corretto con filtro a mediana per la cancellazione fisica delle macchie."""

    @staticmethod
    def estrai_immagine_nativa(percorso, forza_colore=False):
        with rawpy.imread(percorso) as raw:
            try:
                if forza_colore: raise ValueError
                thumb = raw.extract_thumb()
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    im = Image.open(io.BytesIO(thumb.data))
                    return ImageOps.exif_transpose(im)
                raise ValueError
            except Exception:
                rgb = raw.postprocess(half_size=False, use_camera_wb=True, no_auto_bright=False)
                arr = np.clip(rgb, 0, 255).astype(np.uint8)
                return Image.fromarray(arr)

    @staticmethod
    def _rimuovi_macchie_immagine(img: Image.Image, macchie: list) -> Image.Image:
        if not macchie:
            return img
        w, h = img.size
        for x, y, r in macchie:
            if x < 0 or x >= w or y < 0 or y >= h:
                continue
            
            margine_campionamento = r + 6
            x0 = max(0, x - margine_campionamento)
            y0 = max(0, y - margine_campionamento)
            x1 = min(w, x + margine_campionamento)
            y1 = min(h, y + margine_campionamento)
            
            larghezza_box = x1 - x0
            altezza_box = y1 - y0
            if larghezza_box <= 0 or altezza_box <= 0:
                continue
                
            ritaglio = img.crop((x0, y0, x1, y1))
            
            # RISOLTO: Applica il MedianFilter per rimpiazzare i pixel scuri della polvere con quelli chiari circostanti
            dimensione_filtro = int(r * 2 + 1)
            if dimensione_filtro % 2 == 0:
                dimensione_filtro += 1
            ritaglio_pulito = ritaglio.filter(ImageFilter.MedianFilter(size=max(3, dimensione_filtro)))
            
            maschera = Image.new("L", (larghezza_box, altezza_box), 0)
            disegno = ImageDraw.Draw(maschera)
            centro_x = x - x0
            centro_y = y - y0
            disegno.ellipse((centro_x - r, centro_y - r, centro_x + r, centro_y + r), fill=255)
            maschera_sfumata = maschera.filter(ImageFilter.GaussianBlur(radius=3))
            
            ritaglio_corretto = Image.composite(ritaglio_pulito, ritaglio, maschera_sfumata)
            img.paste(ritaglio_corretto, (x0, y0))
        return img

    @staticmethod
    def _ritaglia_bordi_rotazione(img: Image.Image, angolo_gradi: float) -> Image.Image:
        angolo = math.radians(abs(angolo_gradi))
        if angolo == 0: return img
        w_orig, h_orig = img.size
        cos_a, sin_a = math.cos(angolo), math.sin(angolo)
        denom = h_orig * sin_a + w_orig * cos_a
        if denom == 0: return img
        fattore = (h_orig * cos_a - w_orig * sin_a) / denom
        if fattore <= 0: fattore = h_orig / (w_orig * sin_a + h_orig * cos_a)
        new_w, new_h = w_orig * fattore, h_orig * fattore
        img_w, img_h = img.size
        x0, y0 = int((img_w - new_w) / 2.0), int((img_h - new_h) / 2.0)
        return img.crop((x0, y0, int(x0 + new_w), int(y0 + new_h)))

    @staticmethod
    def _correzione_distorsione(img: Image.Image, k1: float) -> Image.Image:
        if abs(k1) < 0.001: return img
        w, h = img.size
        cx, cy = w / 2.0, h / 2.0
        r_max = math.sqrt(cx**2 + cy**2)
        griglia_x, griglia_y = 16, 16
        passo_x, passo_y = w / griglia_x, h / griglia_y
        
        def mappa_punto(x, y):
            dx, dy = x - cx, y - cy
            fattore = 1.0 + k1 * ((math.sqrt(dx**2 + dy**2) / r_max)**2)
            return cx + dx * fattore, cy + dy * fattore

        mesh_data = []
        for i in range(griglia_x):
            for j in range(griglia_y):
                x0, y0 = i * passo_x, j * passo_y
                x1, y1 = x0 + passo_x, y0 + passo_y
                mesh_data.append(((int(x0), int(y0), int(x1), int(y1)), (mappa_punto(x0, y0) + mappa_punto(x0, y1) + mappa_punto(x1, y1) + mappa_punto(x1, y0))))
        return img.transform((w, h), Image.Transform.MESH, mesh_data, resample=Image.Resampling.BILINEAR)

    @staticmethod
    def applica_editing(img_base, b, c, s, sharp, denoise, rotation, distortion, crop, margine, macchie=None, modalita_bw=False):
        img = img_base.copy()

        if macchie:
            img = MotoreSviluppo._rimuovi_macchie_immagine(img, macchie)
        if denoise > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=denoise))
        if abs(distortion) > 0:
            img = MotoreSviluppo._correzione_distorsione(img, distortion)
        if abs(rotation) > 0:
            img = img.rotate(rotation, resample=Image.Resampling.BILINEAR, expand=True)
            img = MotoreSviluppo._ritaglia_bordi_rotazione(img, rotation)
            
        w, h = img.size
        pct_crop, pct_margine = min(0.45, crop / 100.0), min(0.45, margine / 100.0)
        x0, y0 = int(w * (pct_crop + pct_margine)), int(h * (pct_crop + pct_margine))
        x1, y1 = w - x0, h - y0
        
        if x1 > x0 and y1 > y0 and (x0 > 0 or y0 > 0):
            img = img.crop((x0, y0, x1, y1))

        img = ImageEnhance.Brightness(img).enhance(b)
        img = ImageEnhance.Contrast(img).enhance(c)
        img = img.convert("L").convert("RGB") if modalita_bw else ImageEnhance.Color(img).enhance(s)
        if sharp > 0:
            img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=int(sharp), threshold=1))
        return img
```

---

## 📄 File: `esportatore_canali.py`
**Descrizione**: Logica di ricampionamento Stampa, Social, Web e Batch

```python
import os
from PIL import Image
from motore_sviluppo import MotoreSviluppo

class EsportatoreCanali:
    """Gestisce il ricampionamento mirato e l'esportazione batch automatica in cartelle dedicate."""

    @staticmethod
    def _ridimensiona_lato_corto(img: Image.Image, target_corto: int) -> Image.Image:
        w, h = img.size
        if w <= h:
            nuova_w = target_corto
            nuova_h = int(h * (target_corto / w))
        else:
            nuova_h = target_corto
            nuova_w = int(w * (target_corto / h))
        return img.resize((nuova_w, nuova_h), Image.Resampling.LANCZOS)

    @staticmethod
    def elabora_e_salva(canale: str, percorso_raw: str, params: dict, dest_path: str):
        img = MotoreSviluppo.estrai_immagine_nativa(percorso_raw, forza_colore=not params['is_bw'])
        img = MotoreSviluppo.applica_editing(
            img, params['brightness'], params['contrast'], params['saturation'],
            params['sharpness'], params['denoise'], params['rotation'],
            params['distortion'], params['crop'], params['margine'], params['is_bw']
        )

        if canale == "stampa":
            target_corto_px = int((20 / 2.54) * 300)
            img = EsportatoreCanali._ridimensiona_lato_corto(img, target_corto_px)
            img.save(dest_path, "JPEG", quality=100, dpi=(300, 300))
        elif canale == "social":
            img = EsportatoreCanali._ridimensiona_lato_corto(img, 1080)
            img.save(dest_path, "JPEG", quality=100)
        elif canale == "web":
            img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
            img.save(dest_path, "JPEG", quality=98)

    @staticmethod
    def esegui_esportazione_batch(cartella_base: str, coda: list, callback_progresso=None):
        """Genera le tre cartelle di output ed esporta i tre formati, notificando l'avanzamento."""
        dir_stampa = os.path.join(cartella_base, "AutoStampa")
        dir_social = os.path.join(cartella_base, "AutoSocial")
        dir_web = os.path.join(cartella_base, "AutoWeb")

        for d in [dir_stampa, dir_social, dir_web]:
            os.makedirs(d, exist_ok=True)

        for i, (nome_file, params) in enumerate(coda):
            percorso_raw = os.path.join(cartella_base, nome_file)
            nome_puro = os.path.splitext(nome_file)[0]
            
            if not os.path.exists(percorso_raw):
                continue

            # Se presente una callback, aggiorna lo stato visivo prima di iniziare l'elaborazione pesante
            if callback_progresso:
                callback_progresso(i + 1, len(coda), nome_file)

            EsportatoreCanali.elabora_e_salva("stampa", percorso_raw, params, os.path.join(dir_stampa, f"{nome_puro}.jpg"))
            EsportatoreCanali.elabora_e_salva("social", percorso_raw, params, os.path.join(dir_social, f"{nome_puro}.jpg"))
            EsportatoreCanali.elabora_e_salva("web", percorso_raw, params, os.path.join(dir_web, f"{nome_puro}.jpg"))
```

---

## 📄 File: `dialog_esportazione.py`
**Descrizione**: Finestra di dialogo popup per il salvataggio singolo

```python
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from esportatore_canali import EsportatoreCanali

class DialogEsportazioneSingola:
    """Gestisce la finestra popup per la scelta del canale di output della foto corrente."""

    @staticmethod
    def apri(app):
        if not app.collezione.file_attivo:
            return
        app.salva_stato_corrente()
        
        popup = tk.Toplevel(app.root)
        popup.title("Esporta Immagine")
        popup.geometry("340x220")
        popup.resizable(False, False)
        popup.transient(app.root)
        popup.grab_set()
        
        ttk.Label(popup, text="Scegli il profilo di esportazione:", font=("Arial", 10, "bold")).pack(pady=10)
        
        def esegui_scelta(scelta: str):
            popup.destroy()
            params = app.raccogli_parametri_attuali()
            file_attivo = app.collezione.file_attivo
            
            if scelta == "tutte":
                cartella_raw = os.path.dirname(file_attivo)
                coda_singola = [(os.path.basename(file_attivo), params)]
                app.root.config(cursor="watch")
                app.root.update()
                try:
                    EsportatoreCanali.esegui_esportazione_batch(cartella_raw, coda_singola)
                    messagebox.showinfo("Successo", "I 3 file (Stampa, Social, Web) sono stati salvati nelle rispettive cartelle.")
                except Exception as e:
                    messagebox.showerror("Errore", str(e))
                finally:
                    app.root.config(cursor="")
            else:
                nome_base = os.path.splitext(os.path.basename(file_attivo))[0]
                dest = filedialog.asksaveasfilename(
                    defaultextension=".jpg", 
                    filetypes=[("JPEG Image", "*.jpg")], 
                    initialfile=f"{scelta}_{nome_base}.jpg"
                )
                if not dest:
                    return
                app.root.config(cursor="watch")
                app.root.update()
                try:
                    EsportatoreCanali.elabora_e_salva(scelta, file_attivo, params, dest)
                    messagebox.showinfo("Successo", "Esportazione completata!")
                except Exception as e:
                    messagebox.showerror("Errore", str(e))
                finally:
                    app.root.config(cursor="")

        ttk.Button(popup, text="🖨️ Stampa (20x30 cm @300dpi)", command=lambda: esegui_scelta("stampa")).pack(fill=tk.X, padx=20, pady=2)
        ttk.Button(popup, text="📱 Social (Lato corto 1080px)", command=lambda: esegui_scelta("social")).pack(fill=tk.X, padx=20, pady=2)
        ttk.Button(popup, text="🌐 Web (Lato lungo 2048px)", command=lambda: esegui_scelta("web")).pack(fill=tk.X, padx=20, pady=2)
        ttk.Button(popup, text="🚀 Esporta in tutti e 3 i canali", command=lambda: esegui_scelta("tutte")).pack(fill=tk.X, padx=20, pady=8)
```

---

