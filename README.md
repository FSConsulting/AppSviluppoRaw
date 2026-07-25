# Nikon NEF Batch Editor

Questo repository contiene il progetto Python per lo sviluppo e il ritocco batch di file RAW nella cartella `Ver_02`.

## Struttura del progetto

- `Ver_02/app_gui.py`: applicazione principale Tkinter per il caricamento, la visualizzazione e il ritocco dei file RAW.
- `Ver_02/genera_report.py`: script per generare report sul progetto e sui moduli principali.
- `Ver_02/run_app.bat`: script Windows per avviare rapidamente l'applicazione GUI.
- `Ver_02/run_docs.bat`: script Windows per costruire la documentazione Sphinx.
- `Ver_02/run_tests.bat`: script Windows per eseguire i test unitari disponibili.
- `requirements.txt`: dipendenze Python necessarie per eseguire l'applicazione e il progetto.

## Requisiti

Questo progetto è pensato per essere eseguito su Windows con un ambiente Python 3.13+.

Dipendenze principali:

- `rawpy>=0.21.0`
- `Pillow>=10.0.0`
- `numpy>=1.24.0`

Installa tutto con:

```powershell
pip install -r requirements.txt
```

## Uso principale

### Avviare l'applicazione GUI

Apri PowerShell nella root del repository o in `Ver_02`, attiva il virtual environment e lancia il file:

```powershell
cd Ver_02
..\ai_env\Scripts\Activate.ps1
run_app.bat
```

In alternativa:

```powershell
f:\Users\fabrizio\AI_Workspace\ai_env\Scripts\python.exe Ver_02\app_gui.py
```

### Generare un report

Puoi eseguire `genera_report.py` per creare un report sul codice e i moduli del progetto:

```powershell
cd Ver_02
..\ai_env\Scripts\Activate.ps1
python genera_report.py
```

### Costruire la documentazione

La documentazione Sphinx si trova in `Ver_02/docs`. Usa il wrapper:

```powershell
cd Ver_02
..\ai_env\Scripts\Activate.ps1
run_docs.bat
```

### Eseguire i test

Esegui i test unitari presenti in `Ver_02` con:

```powershell
cd Ver_02
..\ai_env\Scripts\Activate.ps1
run_tests.bat
```

## Note

- La cartella `Ver_02` contiene la versione corrente dell'applicazione con i file principali, la documentazione e gli script di utilità.
- Il file `Ver_02/README.md` contiene dettagli specifici sulla versione `Ver_02` del progetto e informazioni supplementari sui workflow della documentazione.
