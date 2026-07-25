"""Persistenza locale basata su SQLite per i parametri foto.

`DatabaseManager` offre operazioni semplici per salvare e recuperare un
JSON serializzato contenente i parametri di sviluppo associati a ogni
file RAW. Viene usato come storage minimale integrato nella cartella di
lavoro.
"""

import sqlite3
import json
import os

class DatabaseManager:
    """Gestore della persistenza SQLite per i parametri di sviluppo dei file RAW."""

    def __init__(self, percorso_db="parametri_sviluppo.db"):
        self.percorso_db = percorso_db
        self.connessione = sqlite3.connect(self.percorso_db, check_same_thread=False)
        self.crea_tabelle()

    def crea_tabelle(self):
        """Inizializza la tabella sul database se non esiste."""
        cursor = self.connessione.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS impostazioni_foto (
                percorso_file TEXT PRIMARY KEY,
                dati_json TEXT
            )
        ''')
        self.connessione.commit()

    def salva_parametri(self, percorso_file: str, parametri: dict):
        """Salva o aggiorna i parametri di sviluppo associati a un file RAW."""
        if not percorso_file:
            return
        try:
            cursor = self.connessione.cursor()
            # Converte il dizionario dei parametri e la lista macchie in stringa JSON
            stringa_json = json.dumps(parametri)
            cursor.execute('''
                INSERT OR REPLACE INTO impostazioni_foto (percorso_file, dati_json)
                VALUES (?, ?)
            ''', (percorso_file, stringa_json))
            self.connessione.commit()
        except Exception:
            pass

    def carica_parametri(self, percorso_file: str) -> dict:
        """Recupera i parametri memorizzati per un determinato file RAW."""
        if not percorso_file:
            return {}
        try:
            cursor = self.connessione.cursor()
            cursor.execute('''
                SELECT dati_json FROM impostazioni_foto WHERE percorso_file = ?
            ''', (percorso_file,))
            riga = cursor.fetchone()
            if riga:
                return json.loads(riga[0])
        except Exception:
            pass
        return {}

    def chiudi(self):
        """Chiude in sicurezza la connessione attiva al database SQLite."""
        if self.connessione:
            try:
                self.connessione.commit()
                self.connessione.close()
            except Exception:
                pass
            finally:
                self.connessione = None
