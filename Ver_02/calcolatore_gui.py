"""Funzioni di utilità per calcoli GUI e esportazioni ad alta risoluzione.

Contiene `CalcolatoreGui` che espone funzioni statiche per calcolare
centrature di zoom sul canvas e per eseguire salvataggi HD dei RAW.
"""

import os
from PIL import Image
from motore_sviluppo import MotoreSviluppo

class CalcolatoreGui:
    """Classe di utilità statica per l'elaborazione dei calcoli della GUI e delle esportazioni HD."""

    @staticmethod
    def calcola_centratura_zoom(px, py, w_vis, h_vis, x_off, y_off, wc, hc):
        """
        Calcola le frazioni di scorrimento (da 0.0 a 1.0) necessarie al Canvas per centrare lo zoom.
        
        :param px: Posizione X relativa del clic sull'immagine (0.0 a 1.0)
        :param py: Posizione Y relativa del clic sull'immagine (0.0 a 1.0)
        :param w_vis: Larghezza dell'immagine visualizzata
        :param h_vis: Altezza dell'immagine visualizzata
        :param x_off: Offset X dell'immagine all'interno del Canvas
        :param y_off: Offset Y dell'immagine all'interno del Canvas
        :param wc: Larghezza corrente del widget Canvas
        :param hc: Altezza corrente del widget Canvas
        :return: Tupla (tx, ty) con le frazioni di scorrimento normalizzate
        """
        # Calcolo dei punti di ancoraggio assoluti sul canvas virtuale
        ancora_x = (px * w_vis) + x_off - (wc / 2)
        ancora_y = (py * h_vis) + y_off - (hc / 2)
        
        # Calcolo dei divisori massimi basati sulla regione di scorrimento totale
        regione_totale_x = max(1, w_vis + (2 * x_off))
        regione_totale_y = max(1, h_vis + (2 * y_off))
        
        # Normalizzazione dei valori tra 0.0 e 1.0 per il metodo xview_moveto/yview_moveto
        tx = ancora_x / regione_totale_x
        ty = ancora_y / regione_totale_y
        
        tx_normalizzato = max(0.0, min(1.0, tx))
        ty_normalizzato = max(0.0, min(1.0, ty))
        
        return tx_normalizzato, ty_normalizzato

    @staticmethod
    def esempio_uso_centratura():
        """Esempio d'uso rapido per testing manuale.

        >>> CalcolatoreGui.calcola_centratura_zoom(0.5, 0.5, 800, 600, 0, 0, 400, 300)
        (0.5, 0.5)
        """

    @staticmethod
    def esegui_salvataggio_hd(percorso, b, c, s, sharp, denoise, rotation, distortion, crop, margine, modalita_bw, dest):
        """
        Esegue lo sviluppo a piena risoluzione del file RAW applicando i parametri scelti dall'utente.
        
        Include filtri base, correzioni avanzate e parametri di ritaglio manuale.
        """
        forza_colore = not modalita_bw
        
        # Estrazione dell'immagine nativa ad alta risoluzione
        img_hd = MotoreSviluppo.estrai_immagine_nativa(percorso, forza_colore=forza_colore)
        
        # Applicazione di tutti i parametri di sviluppo e ritaglio manuale
        img_hd = MotoreSviluppo.applica_editing(
            img_hd, 
            b, 
            c, 
            s, 
            sharp, 
            denoise, 
            rotation, 
            distortion,
            crop,
            margine,
            modalita_bw
        )
        
        # Ridimensionamento ad alta qualità temporaneo (lato lungo a 2048px)
        img_hd.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
        
        # Salvataggio definitivo in JPEG ad altissima qualità
        img_hd.save(dest, "JPEG", quality=98)
