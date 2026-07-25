"""Utility per generare report e file di supporto del progetto.

Fornisce script utili per creare il `requirements.txt` minimale e un
report in formato Markdown che raccoglie i sorgenti principali del
progetto per revisione o upload.
"""

import os

def genera_file_requirements():
    """Genera automaticamente il file requirements.txt con le dipendenze corrette."""
    contenuto_req = (
        "rawpy>=0.21.0\n"
        "Pillow>=10.0.0\n"
        "numpy>=1.24.0\n"
    )
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(contenuto_req)
    print("[✓] File 'requirements.txt' generato con successo.")

def build_report_markdown():
    """Legge tutti i file sorgente del progetto e compila il report avanzamento.md."""
    # Elenco rigoroso di tutti i file dell'architettura OOP che abbiamo sviluppato
    mappa_progetto = [
        ("requirements.txt", "Dipendenze del progetto"),
        ("app_gui.py", "Interfaccia grafica principale e coordinamento"),
        ("componenti_gui.py", "Struttura visiva, widget e slider laterali"),
        ("collezione_manager.py", "Gestione dello stato della lista file RAW"),
        ("interazione_manager.py", "Logica del mouse, drag e zoom sul canvas"),
        ("ritocco_manager.py", "Strumento pennello e coordinate rimozione macchie"),
        ("database_manager.py", "Persistenza SQLite e migrazione dei dati"),
        ("motore_sviluppo.py", "Sviluppo RAW, filtri PIL e rimozione macchie"),
        ("esportatore_canali.py", "Logica di ricampionamento Stampa, Social, Web e Batch"),
        ("dialog_esportazione.py", "Finestra di dialogo popup per il salvataggio singolo")
    ]

    with open("avanzamento.md", "w", encoding="utf-8") as md:
        # Intestazione del Report
        md.write("# 📷 Nikon NEF Batch Editor - Report Avanzamento Progetto\n\n")
        md.write("Questo file contiene lo stato attuale dell'architettura software divisa in moduli compatti.\n\n")
        md.write("## 🗂️ Struttura dei File del Progetto\n\n")
        
        # Generazione dell'indice
        for file_name, desc in mappa_progetto:
            md.write(f"* **`{file_name}`**: {desc}\n")
        md.write("\n---\n\n")

        # Inserimento del codice sorgente di ciascun file
        for file_name, desc in mappa_progetto:
            md.write(f"## 📄 File: `{file_name}`\n")
            md.write(f"**Descrizione**: {desc}\n\n")
            
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as sorgente:
                    codice = sorgente.read()
                
                # Determina l'estensione per la sintassi del blocco markdown
                estensione = "txt" if file_name.endswith(".txt") else "python"
                md.write(f"```{estensione}\n")
                md.write(codice)
                if not codice.endswith("\n"):
                    md.write("\n")
                md.write("```\n\n")
            else:
                md.write("> ⚠️ *Nota: Il file non è stato trovato localmente nella cartella di esecuzione.*\n\n")
            md.write("---\n\n")

    print("[✓] Report 'avanzamento.md' compilato con successo.")


def esempio_generazione_report():
    """Esempio d'uso rapido per generare i file di supporto.

    Questo helper viene usato internamente dallo script ma è utile anche per
    eseguire manualmente le operazioni di creazione del file requirements.
    """
    genera_file_requirements()
    build_report_markdown()

if __name__ == "__main__":
    # Esegue la catena di montaggio del report
    genera_file_requirements()
    build_report_markdown()
    print("\n[FINITO] Puoi caricare i file generati direttamente sul tuo Google Drive!")
