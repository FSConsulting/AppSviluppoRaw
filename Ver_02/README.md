# Ver_02 - Nikon NEF Batch Editor

[![Docs Build](https://github.com/FSConsulting/AppSviluppoRaw/actions/workflows/build-docs.yml/badge.svg)](https://github.com/FSConsulting/AppSviluppoRaw/actions/workflows/build-docs.yml)

Questa cartella contiene la versione **`Ver_02`** dell'applicazione desktop Python/Tkinter per lo sviluppo RAW (`.NEF`), la regolazione dei parametri cromatici/geometrici, il ritocco con pennello macchie ed inpainting, e l'esportazione batch multichannel.

---

## 📌 Obiettivo e Funzionalità Avanzate

* **Sviluppo RAW Non Distruttivo**: Estrazione native RGB tramite `rawpy`, regolazione di luminosità, contrasto, saturazione, nitidezza, denoise e conversione B/W.
* **Geometria e Ritaglio**: Rotazione dinamica dell'angolo (-45° a +45°), distorsione lente, ritaglio orizzontale (Crop %) e margine verticale.
* **🎨 Tema Grafico Darkroom Scuro**: Interfaccia integrata con uno stile scuro uniforme ed elegante (`#1e1e1e` / `#252526`) per una valutazione cromatica ad alto contrasto.
* **📂 Gestione UX dei Pannelli e Spazi**:
  * Pannelli a scomparsa con configurazione predefinita ideale (*Filtra Visualizzazione* e *Sviluppo e Colore* aperti; *Geometria*, *Output* e *Guida* chiusi).
  * Margini verticali ottimizzati senza sprechi di spazio in alto.
* **↺ Reset Rapido degli Slider**: Pulsante `↺` e doppio click sull'etichetta di ciascun parametro per ripristinare il valore di default.
* **🔍 Zoom Centrato al 100%**: Mappatura matematica sottrattiva dell'offset canvas per garantire che il doppio click focalizzi lo zoom esattamente sul punto cliccato.
* **🧹 Pennello Macchie & Undo (`Ctrl+Z`)**:
  * Definizione di punti macchia destinazione/sorgente con correzione via inpainting.
  * Overlay visivo dinamico sul canvas per lo stato attivo dello strumento.
  * **`Ctrl+Z`** per annullare l'ultima macchia applicata.
* **🖼️ Anteprima Lightbox a Schermo Intero (`Ctrl+L`)**: Overlay a tutto schermo con supporto al doppio click e drag.
* **💾 Esportazione Multicanale e Batch**: Canali predefiniti per Stampa (alta risoluzione), Social e Web.

---

## 🛠️ Requisiti e Setup Iniziale

- **Sistema Operativo**: Windows 11 / 10
- **Python**: 3.13+
- **Virtual Environment**: situato in `F:\Users\fabrizio\AI_Workspace\ai_env`

### Setup Ambiente:
1. Apri PowerShell in `F:\Users\fabrizio\AI_Workspace\Ver_02`
2. Attiva il virtual environment:
   ```powershell
   ..\ai_env\Scripts\Activate.ps1
   ```
3. Installa le dipendenze:
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🚀 Avvio dell'Applicazione

La modalità consigliata e immediata su Windows è lo script BAT:

```powershell
cd F:\Users\fabrizio\AI_Workspace\Ver_02
.\run_app.bat
```

In alternativa via comando diretto Python:

```powershell
..\ai_env\Scripts\python.exe app_gui.py
```

---

## ⌨️ Scorciatoie da Tastiera

| Scorciatoia | Azione |
| :--- | :--- |
| **`B`** | Attiva / Disattiva Pennello Macchie |
| **`Ctrl+Z`** | Annulla Ultima Macchia Applicata |
| **`Esc`** | Reset Zoom / Annulla Vista Zoomata / Chiudi Lightbox |
| **`Ctrl+L`** | Apri Anteprima Lightbox Full-Screen |
| **`Ctrl+O`** | Apri Cartella RAW |
| **`Ctrl+Q`** | Salva ed Esci |
| **Frecce ◄ / ►** | Passa alla foto Precedente / Successiva |
| **Doppio Click (su Foto)** | Zoom 100% centrato / Reset Zoom |
| **Doppio Click (su Titolo Slider / Pulsante ↺)** | Reset Slider al valore predefinito |

---

## 🧪 Test Unitari e Verifica

Per eseguire la suite completa di test unitari (trasformazioni di coordinate, layout lightbox e moduli):

```powershell
cd Ver_02
..\ai_env\Scripts\Activate.ps1
.\run_tests.bat
```

Questo eseguirà tutti i test `test_*.py` presenti nella cartella `Ver_02`.

---

## 📄 Architettura dei File in `Ver_02`

* `app_gui.py`: Controller dell'applicazione GUI e gestione degli stati.
* `componenti_gui.py`: Layout visivo, tema Darkroom, sezioni collassabili e tooltip.
* `interazione_manager.py`: Mappatura eventi mouse, doppio click zoom centrato e drag.
* `ritocco_manager.py`: Pennello macchie, trasformazione geometrica inversa e Undo (`Ctrl+Z`).
* `motore_sviluppo.py`: Motore di elaborazione RAW nativo (`rawpy`), filtri PIL e inpainting.
* `collezione_manager.py`: Gestione dello stato dell'elenco foto e dei filtri di selezione.
* `database_manager.py`: Modulo SQLite per il salvataggio persistente dei parametri.
* `esportatore_canali.py`: Ricampionamento e salvataggio batch per Stampa, Social e Web.
* `dialog_esportazione.py`: Finestra popup di esportazione per lo scatto singolo.
* `genera_report.py`: Utilità per generare report sullo stato dei file.
* `run_app.bat`: Script BAT per avviare l'applicazione GUI.
* `run_tests.bat`: Script BAT per eseguire la suite di test.
* `run_docs.bat`: Script BAT per compilare la documentazione Sphinx.

---

## 📚 Documentazione Sphinx

La documentazione API è generata con Sphinx in `Ver_02/docs`.

### Compilazione Locale:
```powershell
cd Ver_02
..\ai_env\Scripts\Activate.ps1
.\run_docs.bat
```
La versione HTML compilata viene salvata in `Ver_02/docs/_build/html`.

### GitHub Actions:
Il workflow `.github/workflows/build-docs.yml` compila automaticamente la documentazione ad ogni push/PR verso `main`/`master` rendendo disponibile l'artefatto `ver02-docs`.
