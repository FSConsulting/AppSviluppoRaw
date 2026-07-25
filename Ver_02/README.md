# Ver_02 - Nikon NEF Batch Editor

[![Docs Build](https://github.com/FSConsulting/AppSviluppoRaw/actions/workflows/build-docs.yml/badge.svg)](https://github.com/FSConsulting/AppSviluppoRaw/actions/workflows/build-docs.yml)


Questa cartella contiene la versione `Ver_02` dell'applicazione GUI per lo sviluppo RAW e il ritocco con pennello macchie.

## Obiettivo
Fornire un'applicazione desktop Python/Tkinter per gestire lo sviluppo di file RAW, zoom in tempo reale e ritocco con un pennello macchie coerente nelle trasformazioni di rotazione e crop.

## Requisiti
- Windows 11
- Python 3.13+ installato
- Virtual environment presente in `ai_env`

## Setup iniziale
1. Apri PowerShell in `F:\Users\fabrizio\AI_Workspace\Ver_02`
2. Attiva l'ambiente virtuale:
   ```powershell
   ..\ai_env\Scripts\Activate.ps1
   ```
3. Installa le dipendenze (se necessario):
   ```powershell
   pip install -r requirements.txt
   ```

> Se il virtual environment non fosse presente, crea l'ambiente in `F:\Users\fabrizio\AI_Workspace\ai_env` e reinstalla le dipendenze.

## Avvio dell'applicazione
La modalità più semplice è usare lo script BAT:

```powershell
cd F:\Users\fabrizio\AI_Workspace\Ver_02
run_app.bat
```

In alternativa puoi avviare direttamente con Python:

```powershell
f:\Users\fabrizio\AI_Workspace\ai_env\Scripts\python.exe app_gui.py
```

## Test e verifica
Per eseguire tutti i test unitari disponibili, usa:

```powershell
cd F:\Users\fabrizio\AI_Workspace\Ver_02
run_tests.bat
```

Questo esegue tutti i file `test_*.py` presenti nella cartella `Ver_02`.

## File principali
- `app_gui.py`: interfaccia grafica dell'applicazione
- `ritocco_manager.py`: logica del pennello macchie e trasformazione coordinate
- `motore_sviluppo.py`: sviluppo RAW, rotazione, crop e ritocco immagine
- `test_ritocco_manager.py`: test unitari per le trasformazioni di coordinate
- `run_app.bat`: script per avviare l'applicazione
- `run_tests.bat`: script per eseguire i test unitari
- `requirements.txt`: dipendenze Python

## Primo utilizzo
1. Avvia `run_app.bat`
2. Carica una cartella RAW con il pulsante `Carica Cartella` o simile
3. Usa il doppio click per ingrandire e zoomare
4. Attiva il pennello macchie e prova i click nelle aree con rotazione/crop per verificare la coerenza delle coordinate
5. Usa il pulsante “Anteprima Lightbox” o `Ctrl+L` per aprire un overlay a schermo intero dell'immagine corrente

## Documentazione

La documentazione API e il manuale veloce sono generati con Sphinx nella cartella `docs/`.

Costruzione locale:

```powershell
cd Ver_02
..\ai_env\Scripts\Activate.ps1
pip install -r requirements.txt
run_docs.bat
```

La versione HTML risultante sarà disponibile in `Ver_02/docs/_build/html`.

GitHub Actions:

Abbiamo aggiunto un workflow che costruisce la documentazione su ogni push/PR verso `main`/`master` e carica l'artefatto `ver02-docs`.

Per pubblicare su GitHub Pages, configura la sorgente Pages sulla cartella `Ver_02/docs/_build/html` oppure aggiungi un job di deploy nella workflow.

## Note
- Usa `Ctrl+L` per aprire rapidamente l'anteprima lightbox oltre al pulsante nella GUI
- La chiusura dell'app dal bottone GUI è gestita in modo pulito e salva lo stato corrente
- I test sono già stati verificati con `unittest` e risultano passati
- Se installi il progetto su un altro PC, assicurati di aggiornare il percorso dell'ambiente virtuale o usa un nuovo venv
