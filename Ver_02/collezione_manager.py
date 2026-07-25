"""Gestione della collezione di file RAW e persistenza dei parametri.

Contiene `CollezioneManager` che mantiene l'elenco completo dei file
RAW di una cartella, applica filtri (tutti/solo selezionati/solo non
selezionati) e coordina l'accesso al `DatabaseManager` per caricare e
salvare parametri di sviluppo per ogni file.
"""

import os
from database_manager import DatabaseManager

class CollezioneManager:
    """Gestore dello stato, della navigazione e dei filtri sulla lista dei file RAW."""

    def __init__(self):
        self.lista_file_completa = []  # Mantiene sempre l'intera cartella in memoria
        self.lista_file = []           # Lista attualmente navigabile (filtrata)
        self.indice_attivo = -1
        self.file_attivo = None
        self.db_manager = None
        self.cartella_corrente = ""

    def inizializza_cartella(self, cartella: str) -> bool:
        """Scansiona la cartella ed estrae l'elenco iniziale dei file RAW."""
        if not cartella or not os.path.isdir(cartella):
            return False

        file_trovati = [
            os.path.join(cartella, f) for f in os.listdir(cartella)
            if f.lower().endswith('.nef')
        ]

        if not file_trovati:
            return False

        self.cartella_corrente = cartella
        self.lista_file_completa = sorted(file_trovati)
        
        percorso_db = os.path.join(cartella, "parametri_sviluppo.db")
        self.db_manager = DatabaseManager(percorso_db)

        # Di default all'avvio carichiamo tutti i file senza filtri
        self.applica_filtro_collezione("Tutti i RAW")
        return True

    def applica_filtro_collezione(self, tipo_filtro: str):
        """Filtra la lista dei file navigabili in base allo stato registrato nel DB."""
        if not self.lista_file_completa:
            return

        vecchio_attivo = self.file_attivo

        if tipo_filtro == "Tutti i RAW":
            self.lista_file = list(self.lista_file_completa)
        else:
            nuova_lista = []
            for file_raw in self.lista_file_completa:
                par = self.db_manager.carica_parametri(file_raw)
                incluso = par.get('esportare', True) if par else True

                if tipo_filtro == "Solo selezionati" and incluso:
                    nuova_lista.append(file_raw)
                elif tipo_filtro == "Solo NON selezionati" and not incluso:
                    nuova_lista.append(file_raw)
            
            self.lista_file = nuova_lista

        if vecchio_attivo in self.lista_file:
            self.indice_attivo = self.lista_file.index(vecchio_attivo)
        elif self.lista_file:
            self.indice_attivo = 0
        else:
            self.indice_attivo = -1

        self.file_attivo = self.lista_file[self.indice_attivo] if self.indice_attivo != -1 else None

    def avanti(self) -> bool:
        """Sposta l'indice sul file successivo nella lista filtrata."""
        if self.lista_file and self.indice_attivo < len(self.lista_file) - 1:
            self.indice_attivo += 1
            self.file_attivo = self.lista_file[self.indice_attivo]
            return True
        return False

    def indietro(self) -> bool:
        """Sposta l'indice sul file precedente nella lista filtrata."""
        if self.lista_file and self.indice_attivo > 0:
            self.indice_attivo -= 1
            self.file_attivo = self.lista_file[self.indice_attivo]
            return True
        return False

    def vai_alla_prima(self) -> bool:
        """Sposta direttamente la selezione sul primo file della lista attiva."""
        if self.lista_file:
            self.indice_attivo = 0
            self.file_attivo = self.lista_file[self.indice_attivo]
            return True
        return False

    def vai_all_ultima(self) -> bool:
        """Sposta direttamente la selezione sull'ultimo file della lista attiva."""
        if self.lista_file:
            self.indice_attivo = len(self.lista_file) - 1
            self.file_attivo = self.lista_file[self.indice_attivo]
            return True
        return False

    def ottieni_testo_info(self) -> str:
        """Genera la stringa informativa da mostrare nella GUI."""
        if not self.file_attivo:
            return "Nessun file corrispondente al filtro impostato"
        
        nome_file = os.path.basename(self.file_attivo)
        totale = len(self.lista_file)
        corrente = self.indice_attivo + 1
        
        return f"File [{corrente}/{totale}]:\n{nome_file}"
