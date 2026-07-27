"""Ritocco e gestione del pennello "macchie".

Questo modulo contiene `RitoccoManager`, l'oggetto responsabile della
logica del pennello per rimuovere macchie/sensore e della trasformazione
tra coordinate native dell'immagine e coordinate di visualizzazione
tenendo conto di rotazione, crop e scaling.
"""

import tkinter as tk
import math

class RitoccoManager:
    """Gestore del pennello macchie con calcolo geometrico a matrici inverse condizionate."""

    def __init__(self, app):
        self.app = app
        self.attivo = False
        self.macchie = []  # Tuple: (dest_x, dest_y, sorg_x, sorg_y, raggio)
        self.raggio_pennello = 20.0
        self.id_cursore_mobile = None
        self.macchia_attiva_dest = None
        self.indice_macchia_in_trascinamento = -1 

    def switch_stato(self):
        """Alterna lo stato del pennello macchie (on/off) e collega gli eventi.

        Quando attivo, il pennello intercetta click, drag e movimento mouse
        per consentire la selezione e la definizione delle macchie da rimuovere.
        """
        cb = self.app.canvas_foto
        self.attivo = not self.attivo
        if self.attivo:
            self.macchia_attiva_dest = None
            self.indice_macchia_in_trascinamento = -1
            cb.bind("<Button-1>", self.gestisci_click_pennello, add="+")
            cb.bind("<B1-Motion>", self.gestisci_trascinamento_sorgente)
            cb.bind("<ButtonRelease-1>", self.gestisci_rilascio_sorgente)
            cb.bind("<Double-Button-1>", self.conclui_macchia_corrente)
            cb.bind("<Motion>", self.aggiorna_posizione_pennello)
            cb.bind("<MouseWheel>", self.gestisci_rotella_pennello)
            cb.config(cursor="none")
        else:
            self.disattivare_stato_pennello()

    def conclui_macchia_corrente(self, event=None):
        """Termina la definizione della macchia attiva (usato su doppio-click)."""
        if self.macchia_attiva_dest is not None:
            self.macchia_attiva_dest = None
            if event: self.aggiorna_posizione_pennello(event)

    def disattiva(self):
        self.disattivare_stato_pennello(forza_salvataggio=False)

    def disattivare_stato_pennello(self, forza_salvataggio=True):
        """Ripristina i binding originali del canvas e salva lo stato se richiesto."""
        self.attivo = False
        self.macchia_attiva_dest = None
        self.indice_macchia_in_trascinamento = -1
        cb = self.app.canvas_foto
        cb.bind("<Button-1>", self.app.interazione.inizia_trascinamento)
        cb.bind("<B1-Motion>", self.app.interazione.esegui_trascinamento)
        cb.bind("<Double-Button-1>", self.app.interazione.gestisci_doppio_click)
        cb.unbind("<ButtonRelease-1>")
        cb.unbind("<Motion>")
        cb.bind_all("<MouseWheel>", lambda e: self.app.canvas_controlli.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        cb.config(cursor="")
        self.cancella_cursore_mobile()
        if forza_salvataggio and hasattr(self.app, 'salva_stato_corrente'):
            self.app.salva_stato_corrente()

    def cancella_cursore_mobile(self):
        if self.id_cursore_mobile:
            self.app.canvas_foto.delete(self.id_cursore_mobile)
            self.id_cursore_mobile = None

    def ottieni_coordinate_reali_mouse(self, event):
        """Calcola le coordinate reali sulla regione di scroll a partire dall'evento mouse.

        Restituisce una tupla ``(cx, cy)`` con le coordinate effettive sul canvas virtuale
        che include l'offset di scroll attuale.
        """
        x_scroll_start, _ = self.app.canvas_foto.xview()
        y_scroll_start, _ = self.app.canvas_foto.yview()
        scrollregion = self.app.canvas_foto.cget("scrollregion").split()
        w_totale_scroll = float(scrollregion[2]) if len(scrollregion) == 4 else self.app.w_visualizzato
        h_totale_scroll = float(scrollregion[3]) if len(scrollregion) == 4 else self.app.h_visualizzato
        cx = (x_scroll_start * w_totale_scroll) + event.x
        cy = (y_scroll_start * h_totale_scroll) + event.y
        return cx, cy

    def aggiorna_posizione_pennello(self, event):
        """Disegna il cursore del pennello sul canvas adattandone il raggio allo scale.

        Viene creato un elemento ovale temporaneo (`id_cursore_mobile`) che segue il mouse.
        """
        if not self.attivo or not self.app.img_anteprima_base: return
        self.cancella_cursore_mobile()
        cx, cy = self.ottieni_coordinate_reali_mouse(event)

        params = self._ottieni_parametri_trasformazione()
        scale = params['scale_x'] if params is not None else 1.0
        rad_vis = max(4, self.raggio_pennello * scale)

        colore = "#ff3333" if self.macchia_attiva_dest is None else "#00bfff"
        self.id_cursore_mobile = self.app.canvas_foto.create_oval(
            cx - rad_vis, cy - rad_vis, cx + rad_vis, cy + rad_vis,
            outline=colore, width=1, dash=(4, 2)
        )

    def gestisci_rotella_pennello(self, event):
        if not self.attivo: return
        self.raggio_pennello = min(150.0, max(5.0, self.raggio_pennello + (2.0 if event.delta > 0 else -2.0)))
        self.aggiorna_posizione_pennello(event)

    def _ottieni_parametri_trasformazione(self):
        if not self.app.img_anteprima_base:
            return None

        w_orig, h_orig = self.app.img_anteprima_base.size
        rotation = self.app.sld_rotation.get()
        crop = self.app.sld_crop.get()
        margine = self.app.sld_margine.get()

        if abs(rotation) > 0.0:
            rad = math.radians(abs(rotation))
            w_rot = abs(w_orig * math.cos(rad)) + abs(h_orig * math.sin(rad))
            h_rot = abs(w_orig * math.sin(rad)) + abs(h_orig * math.cos(rad))
        else:
            w_rot, h_rot = float(w_orig), float(h_orig)

        offset_w = int(w_rot * (crop / 200.0))
        offset_h = int(h_rot * (margine / 200.0))
        w_crop = max(1.0, w_rot - 2.0 * offset_w)
        h_crop = max(1.0, h_rot - 2.0 * offset_h)

        scale_x = self.app.w_visualizzato / w_crop if w_crop > 0.0 else 1.0
        scale_y = self.app.h_visualizzato / h_crop if h_crop > 0.0 else 1.0

        return {
            'w_orig': float(w_orig), 'h_orig': float(h_orig),
            'rotation': rotation, 'rad': math.radians(rotation),
            'w_rot': float(w_rot), 'h_rot': float(h_rot),
            'offset_w': float(offset_w), 'offset_h': float(offset_h),
            'w_crop': float(w_crop), 'h_crop': float(h_crop),
            'scale_x': float(scale_x), 'scale_y': float(scale_y)
        }

    def native_to_screen_coords(self, native_x, native_y):
        params = self._ottieni_parametri_trasformazione()
        if not params:
            return native_x, native_y

        dx = native_x - (params['w_orig'] / 2.0)
        dy = native_y - (params['h_orig'] / 2.0)

        if abs(params['rotation']) > 0.0:
            x_rot = dx * math.cos(params['rad']) - dy * math.sin(params['rad']) + (params['w_rot'] / 2.0)
            y_rot = dx * math.sin(params['rad']) + dy * math.cos(params['rad']) + (params['h_rot'] / 2.0)
        else:
            x_rot, y_rot = native_x, native_y

        x_crop = x_rot - params['offset_w']
        y_crop = y_rot - params['offset_h']

        return x_crop * params['scale_x'], y_crop * params['scale_y']

    def traduci_schermo_a_pixel_nativo(self, cx, cy):
        """Inverte matematicamente crop e rotazione considerando l'espansione dei bordi di PIL."""
        params = self._ottieni_parametri_trasformazione()
        if not params:
            return 0.0, 0.0

        x_crop = cx / params['scale_x'] if params['scale_x'] != 0.0 else cx
        y_crop = cy / params['scale_y'] if params['scale_y'] != 0.0 else cy
        x_rot = x_crop + params['offset_w']
        y_rot = y_crop + params['offset_h']

        if abs(params['rotation']) > 0.0:
            dx = x_rot - (params['w_rot'] / 2.0)
            dy = y_rot - (params['h_rot'] / 2.0)
            cos_a = math.cos(params['rad'])
            sin_a = math.sin(params['rad'])
            real_x = dx * cos_a + dy * sin_a + (params['w_orig'] / 2.0)
            real_y = -dx * sin_a + dy * cos_a + (params['h_orig'] / 2.0)
        else:
            real_x, real_y = x_rot, y_rot

        return max(0.0, min(params['w_orig'], real_x)), max(0.0, min(params['h_orig'], real_y))

    def gestisci_click_pennello(self, event):
        """Gestisce il click principale: inizio/fine definizione macchia o rimozione.

        Logica:
        - se il click è vicino a una sorgente esistente, abilita il drag di sorgente
        - se il click è vicino alla destinazione, rimuove la macchia
        - altrimenti crea una nuova macchia con sorgente di default
        """
        if not self.attivo or not self.app.img_anteprima_base: return
        canvas_x, canvas_y = self.ottieni_coordinate_reali_mouse(event)

        if 0 <= canvas_x <= self.app.w_visualizzato and 0 <= canvas_y <= self.app.h_visualizzato:
            real_x, real_y = self.traduci_schermo_a_pixel_nativo(canvas_x, canvas_y)
            soglia = self.raggio_pennello * 1.5

            for i, m in enumerate(self.macchie):
                if len(m) == 5:
                    _, _, sx, sy, _ = m
                elif len(m) == 3:
                    _, _, raggio = m
                    sx = max(0.0, m[0] - raggio * 2)
                    sy = m[1]
                else:
                    continue
                if ((sx - real_x)**2 + (sy - real_y)**2)**0.5 < soglia:
                    self.indice_macchia_in_trascinamento = i
                    return 

            macchia_da_rimuovere = None
            for m in self.macchie:
                if len(m) == 5:
                    dx, dy, _, _, _ = m
                elif len(m) == 3:
                    dx, dy, _ = m
                else:
                    continue
                if ((dx - real_x)**2 + (dy - real_y)**2)**0.5 < soglia:
                    macchia_da_rimuovere = m
                    break

            if macchia_da_rimuovere:
                self.macchie.remove(macchia_da_rimuovere)
                self.macchia_attiva_dest = None
                self.app.disegna_indicatori_macchie()
                self.app.aggiorna_anteprima()
                return

            if self.macchia_attiva_dest is None:
                self.macchia_attiva_dest = (real_x, real_y)
                sorg_x_def = max(0.0, real_x - self.raggio_pennello * 2)
                self.macchie.append((real_x, real_y, sorg_x_def, real_y, self.raggio_pennello))
            else:
                if self.macchie:
                    dx, dy, _, _, r = self.macchie[-1]
                    self.macchie[-1] = (dx, dy, real_x, real_y, r)
                self.macchia_attiva_dest = None

            self.app.disegna_indicatori_macchie()
            self.app.aggiorna_anteprima()
            self.app.root.after(10, lambda: self.aggiorna_posizione_pennello(event))

    def gestisci_trascinamento_sorgente(self, event):
        if not self.attivo or self.indice_macchia_in_trascinamento == -1 or not self.app.img_anteprima_base: return
        canvas_x, canvas_y = self.ottieni_coordinate_reali_mouse(event)
        canvas_x = max(0.0, min(self.app.w_visualizzato, canvas_x))
        canvas_y = max(0.0, min(self.app.h_visualizzato, canvas_y))
        
        real_x, real_y = self.traduci_schermo_a_pixel_nativo(canvas_x, canvas_y)
        mx_orig, my_orig, _, _, raggio_orig = self.macchie[self.indice_macchia_in_trascinamento]
        self.macchie[self.indice_macchia_in_trascinamento] = (mx_orig, my_orig, real_x, real_y, raggio_orig)
        
        self.app.disegna_indicatori_macchie()
        self.app.aggiorna_anteprima()
        self.aggiorna_pennello_posizione(event)

    def aggiorna_pennello_posizione(self, event):
        self.aggiorna_posizione_pennello(event)

    def gestisci_rilascio_sorgente(self, event):
        if self.indice_macchia_in_trascinamento != -1:
            self.indice_macchia_in_trascinamento = -1
            self.app.disegna_indicatori_macchie()
            self.app.aggiorna_anteprima()

    def annulla_ultima_macchia(self):
        """Rimuove l'ultima macchia aggiunta (Undo / Ctrl+Z)."""
        if self.macchie:
            self.macchie.pop()
            self.macchia_attiva_dest = None
            self.app.disegna_indicatori_macchie()
            self.app.aggiorna_anteprima()
            if hasattr(self.app, 'salva_stato_corrente'):
                self.app.salva_stato_corrente()
            self.app.set_status("Ultima macchia annullata (Ctrl+Z).")
        else:
            self.app.set_status("Nessuna macchia da annullare.")

