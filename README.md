# 📷 Nikon NEF Batch Editor (`AppSviluppoRaw`)

Applicazione Desktop avanzata in Python/Tkinter per il caricamento, la visualizzazione, lo sviluppo non distruttivo e il ritocco batch di file RAW Nikon (`.NEF`).

---

## 🚀 Novità e Caratteristiche Principali

* **🎨 Tema Grafico Darkroom Scuro**: Interfaccia ridisegnata con uno stile scuro uniforme ed elegante (tonalità `#1e1e1e` / `#252526`) specifico per l'editing fotografico, coordinata tra canvas foto, controlli TTK, pulsanti, scrollbar e barra di stato.
* **📂 Organizzazione UX Ottimizzata**:
  * Pannelli a scomparsa con apertura predefinita mirata (*Filtra Visualizzazione* e *Sviluppo e Colore* aperti; *Geometria*, *Output* e *Guida* chiusi).
  * Recupero massimo dello spazio verticale nel pannello laterale sinistro.
* **↺ Reset Rapido dei Parametri**:
  * Pulsante `↺` presente su tutti gli slider per il ripristino immediato dei valori predefiniti.
  * Supporto al **doppio click sulle etichette degli slider** per il reset rapido.
* **🔍 Zoom Centrato al 100% sul Punto Cliccato**:
  * Mappatura matematica e sottrattiva precisa delle coordinate Canvas per garantire che il doppio click concentri lo zoom esattamente sul dettaglio selezionato.
* **🧹 Pennello Macchie e Undo (Ctrl+Z)**:
  * Strumento di rimozione difetti/sensore con inpainting.
  * Overlay visivo dinamico sul canvas quando il pennello o lo zoom sono attivi.
  * Supporto all'**Undo (`Ctrl+Z`)** per annullare le macchie applicate.
* **⌨️ Scorciatoie da Tastiera**:
  * **`B`**: Attiva/Disattiva Pennello Macchie.
  * **`Ctrl+Z`**: Annulla ultima macchia.
  * **`Esc`**: Resetta zoom / chiude overlay.
  * **`Ctrl+L`**: Anteprima Lightbox a schermo intero.
  * **`Ctrl+O`**: Apri cartella RAW.
  * **Frecce ◄ / ►**: Navigazione tra le immagini.

---

## 🗂️ Struttura del Progetto (`Ver_02`)

Tutto il codice sorgente consolidato e modulare si trova nella cartella **`Ver_02`**:

* **`Ver_02/app_gui.py`**: Controller principale dell'applicazione Tkinter.
* **`Ver_02/componenti_gui.py`**: Layout visivo, tema grafico Darkroom scuro, widget helper, sezioni collassabili e tooltip.
* **`Ver_02/interazione_manager.py`**: Gestione degli eventi mouse, calcolo delle coordinate di zoom centrato e drag canvas.
* **`Ver_02/ritocco_manager.py`**: Gestore del pennello macchie, trasformazione geometrica delle coordinate (rotazione/crop) e Undo (`Ctrl+Z`).
* **`Ver_02/motore_sviluppo.py`**: Sviluppo RAW nativo con `rawpy`, applicazione filtri PIL, rotazione, crop ed inpainting.
* **`Ver_02/collezione_manager.py`**: Gestione dello stato dell'elenco dei file e dei filtri di selezione.
* **`Ver_02/database_manager.py`**: Persistenza SQLite dei parametri di sviluppo e ritocco.
* **`Ver_02/esportatore_canali.py` & `dialog_esportazione.py`**: Logica e finestra per l'esportazione singola e batch nei canali Stampa, Social e Web.
* **`Ver_02/run_app.bat`**: Script Windows raccomandato per l'avvio immediato dell'applicazione GUI.
* **`Ver_02/run_tests.bat`**: Executable per la suite di test unitari con `unittest`.

---

## 🛠️ Requisiti e Installazione

* **Sistema Operativo**: Windows 10 / 11
* **Python**: 3.13+
* **Ambiente Virtuale**: `ai_env` nella root del progetto.

### Dipendenze principali (`requirements.txt`):
* `rawpy>=0.21.0`
* `Pillow>=10.0.0`
* `numpy>=1.24.0`

Installa le dipendenze con:
```powershell
pip install -r requirements.txt
```

---

## ⚡ Guida all'Uso

### 1. Avviare l'Applicazione GUI
Il modo più semplice e veloce su Windows è fare doppio click su `run_app.bat` nella cartella `Ver_02` oppure eseguire da PowerShell:

```powershell
cd Ver_02
.\run_app.bat
```

In alternativa:
```powershell
..\ai_env\Scripts\python.exe Ver_02\app_gui.py
```

### 2. Eseguire la Suite di Test
Per verificare la correttezza dei moduli e delle trasformazioni geometriche:

```powershell
cd Ver_02
..\ai_env\Scripts\Activate.ps1
.\run_tests.bat
```

---

## 📝 Note sulla Documentazione
I dettagli specifici sui workflow Sphinx e sulle pipeline si trovano in `Ver_02/README.md` e nella cartella `Ver_02/docs/`.
