"""Gestione delle interazioni utente sul canvas.

Fornisce `InterazioneManager` per gestire eventi del mouse quali doppio
click per zoom, trascinamento e annulla-zoom. È un wrapper sottile che
mantiene l'app principale separata dalle azioni di input.
"""

import tkinter as tk

class InterazioneManager:
    """Gestore delle interazioni del mouse, dello zoom e del drag sul canvas."""

    def __init__(self, app):
        self.app = app

    def gestisci_doppio_click(self, event):
        """Calcola la coordinata ed effettua uno zoom ad alta risoluzione centrato."""
        if not self.app.img_anteprima_base:
            return

        canvas_x = self.app.canvas_foto.canvasx(event.x)
        canvas_y = self.app.canvas_foto.canvasy(event.y)
        
        click_x_su_foto = canvas_x - self.app.x_offset_canvas
        click_y_su_foto = canvas_y - self.app.y_offset_canvas

        if 0 <= click_x_su_foto <= self.app.w_visualizzato and 0 <= click_y_su_foto <= self.app.h_visualizzato:
            w_orig, h_orig = self.app.img_anteprima_base.size

            self.app.interazione_zoom_x = int((click_x_su_foto / self.app.w_visualizzato) * w_orig)
            self.app.interazione_zoom_y = int((click_y_su_foto / self.app.h_visualizzato) * h_orig)

            # Salva le percentuali esatte del click rispetto alla foto per la centratura successiva
            self.app.zoom_pct_x = click_x_su_foto / self.app.w_visualizzato
            self.app.zoom_pct_y = click_y_su_foto / self.app.h_visualizzato

            self.app.in_zoom = not self.app.in_zoom
            self.app.aggiorna_anteprima()

    def annulla_zoom(self, event=None):
        if self.app.in_zoom:
            self.app.in_zoom = False
            self.app.aggiorna_anteprima()

    def inizia_trascinamento(self, event):
        if self.app.in_zoom:
            self.app.canvas_foto.scan_mark(event.x, event.y)

    def esegui_trascinamento(self, event):
        if self.app.in_zoom:
            self.app.canvas_foto.scan_dragto(event.x, event.y, gain=1)
