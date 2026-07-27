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

        if self.app.in_zoom:
            self.app.in_zoom = False
            self.app.aggiorna_anteprima()
            return

        canvas_x = self.app.canvas_foto.canvasx(event.x)
        canvas_y = self.app.canvas_foto.canvasy(event.y)
        
        canvas_w = max(1, self.app.canvas_foto.winfo_width())
        canvas_h = max(1, self.app.canvas_foto.winfo_height())

        # Offset reale dell'immagine centrata nel canvas quando non è zoomata
        offset_x = max(0, (canvas_w - self.app.w_visualizzato) // 2)
        offset_y = max(0, (canvas_h - self.app.h_visualizzato) // 2)

        click_x_su_foto = canvas_x - offset_x
        click_y_su_foto = canvas_y - offset_y

        if 0 <= click_x_su_foto <= self.app.w_visualizzato and 0 <= click_y_su_foto <= self.app.h_visualizzato:
            pct_x = click_x_su_foto / self.app.w_visualizzato if self.app.w_visualizzato > 0 else 0.5
            pct_y = click_y_su_foto / self.app.h_visualizzato if self.app.h_visualizzato > 0 else 0.5

            self.app.zoom_pct_x = max(0.0, min(1.0, pct_x))
            self.app.zoom_pct_y = max(0.0, min(1.0, pct_y))

            w_orig, h_orig = self.app.img_anteprima_base.size
            self.app.interazione_zoom_x = int(self.app.zoom_pct_x * w_orig)
            self.app.interazione_zoom_y = int(self.app.zoom_pct_y * h_orig)

            self.app.in_zoom = True
            self.app.aggiorna_anteprima()
        else:
            self.app.zoom_pct_x = 0.5
            self.app.zoom_pct_y = 0.5
            self.app.in_zoom = True
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
