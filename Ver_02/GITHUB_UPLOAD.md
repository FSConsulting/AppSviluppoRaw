# GitHub Upload - Ver_02

Questa guida descrive i passaggi consigliati per preparare e caricare su GitHub la cartella `Ver_02`.

## Contenuto consigliato nel repository
- `app_gui.py`
- `componenti_gui.py`
- `interazione_manager.py`
- `ritocco_manager.py`
- `motore_sviluppo.py`
- `test_ritocco_manager.py`
- `run_app.bat`
- `run_tests.bat`
- `README.md`
- `requirements.txt`

## Passaggi per l'upload
1. Apri PowerShell nella cartella `Ver_02`:
   ```powershell
   cd F:\Users\fabrizio\AI_Workspace\Ver_02
   ```
2. Inizializza un repository Git (se non già fatto):
   ```powershell
   git init
   ```
3. Aggiungi i file al repository:
   ```powershell
   git add .
   ```
4. Crea un commit iniziale:
   ```powershell
   git commit -m "Inizializzazione Ver_02 con GUI, ritocco e test"
   ```
5. Aggiungi il remote GitHub (sostituisci con l'URL corretto):
   ```powershell
   git remote add origin https://github.com/tuo-utente/tuo-repo.git
   ```
6. Esegui il push sul branch principale:
   ```powershell
   git branch -M main
   git push -u origin main
   ```

## Suggerimenti per il repository
- Mantieni la cartella `ai_env` esclusa da Git con `.gitignore`
- Includi `requirements.txt` per ricreare l'ambiente
- Aggiungi istruzioni chiare in `README.md` per setup e avvio
- Inserisci solo i file sorgente necessari: evita file temporanei di editor o build

## `.gitignore` consigliato
```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo

# Virtual environment
ai_env/

# File di sistema
Thumbs.db
.DS_Store

# Editor
.vscode/
.idea/
```

## Verifica post-upload
- Dopo il push, verifica il repository da GitHub
- Controlla che `README.md` e `run_app.bat` siano visibili
- Verifica che `GITHUB_UPLOAD.md` sia disponibile come guida per i collaboratori
