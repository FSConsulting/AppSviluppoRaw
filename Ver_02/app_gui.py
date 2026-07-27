"""Main GUI application for Nikon NEF Batch Editor (Ver_02).

This module defines `AppSviluppoRaw`, the primary Tkinter application
controller that wires together UI components, user interactions and the
image development/retouching engine.

Only core public methods are documented here; private helpers contain
inline comments where necessary.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading


def calcola_layout_lightbox(canvas_w, canvas_h, img_w, img_h, focus_x=0.5, focus_y=0.5, zoom_attivo=False):
    """Calcola posizione e scrollregion per una lightbox con supporto zoom/pan.

    Quando l'immagine è visualizzata a 100% il canvas deve avere una scrollregion
    che copra sia il bordo sinistro/superiore negativo sia il bordo destro/inferiore
    dell'immagine. In questo modo non si verifica il clipping del contenuto quando
    il punto di focus spinge l'immagine fuori dal viewport.
    """
    canvas_w = max(1, int(canvas_w))
    canvas_h = max(1, int(canvas_h))
    img_w = max(1, int(img_w))
    img_h = max(1, int(img_h))

    if zoom_attivo:
        viewport_w = canvas_w
        viewport_h = canvas_h
        x_pos = int(viewport_w / 2 - focus_x * img_w)
        y_pos = int(viewport_h / 2 - focus_y * img_h)
        left = min(0, x_pos)
        top = min(0, y_pos)
        right = max(viewport_w, x_pos + img_w)
        bottom = max(viewport_h, y_pos + img_h)
        scrollregion = (left, top, right, bottom)
        return x_pos, y_pos, scrollregion

    display_w = min(img_w, canvas_w)
    display_h = min(img_h, canvas_h)
    x_pos = max(0, (canvas_w - display_w) // 2)
    y_pos = max(0, (canvas_h - display_h) // 2)
    scrollregion = (0, 0, max(display_w, canvas_w), max(display_h, canvas_h))
    return x_pos, y_pos, scrollregion

from motore_sviluppo import MotoreSviluppo
from componenti_gui import ComponentiGui
from collezione_manager import CollezioneManager
from interazione_manager import InterazioneManager
from ritocco_manager import RitoccoManager
from dialog_esportazione import DialogEsportazione
from esportatore_canali import EsportatoreCanali

class AppSviluppoRaw:
    """Controller principale dell'applicazione Tkinter.

    Responsabilità:
    - inizializzare i componenti UI in :mod:`componenti_gui`
    - collegare il :class:`RitoccoManager`, :class:`InterazioneManager` e :class:`CollezioneManager`
    - orchestrare caricamento immagine, salvataggio stato e aggiornamento preview

    Note
    ----
    Molti metodi UI (es. ``aggiorna_anteprima``, ``salva_stato_corrente``)
    sono progettati per essere idempotenti e sicuri rispetto a chiamate ripetute
    dall'interfaccia utente (debounce e lock dove necessario).

    .. rubric:: Esempio

    .. code-block:: console

        cd Ver_02
        ../ai_env/Scripts/Activate.ps1
        python app_gui.py

    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Nikon NEF Batch Editor")
        self.root.geometry("1200x800")
        
        self.collezione = CollezioneManager()
        self.interazione = InterazioneManager(self)
        self.ritocco = RitoccoManager(self)
        
        self.img_anteprima_base = self.tk_foto = None
        self.in_zoom = False
        self.w_visualizzato = self.h_visualizzato = 1
        self.x_offset_canvas = self.y_offset_canvas = 0
        
        self.interazione_zoom_x = 0
        self.interazione_zoom_y = 0
        self.zoom_pct_x = 0.5
        self.zoom_pct_y = 0.5
        
        self.parametri_ultimo_scatto_sviluppato = {}
        
        self._thread_elaborazione = None
        self._lock_elaborazione = threading.Lock()
        self._resize_debounce_id = None
        
        ComponentiGui.crea_layout(self)
        ComponentiGui.crea_menu(self)
        ComponentiGui.crea_controlli(self)
        self.configura_bindings()
        self.root.protocol("WM_DELETE_WINDOW", self.gestisci_chiusura_app)
        self.portare_in_primo_piano()

    def portare_in_primo_piano(self):
        """Forza la finestra principale dell'applicazione in primo piano e con focus visibile."""
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after(150, lambda: self.root.attributes("-topmost", False))
            self.root.focus_force()
        except Exception:
            pass

        
    def configure_bindings(self):
        self.configura_bindings()

    def set_status(self, testo: str):
        """Aggiorna la barra di stato dell'app.

        Args:
            testo: Testo da mostrare nella label di stato.
        """
        if hasattr(self, 'lbl_stato'):
            self.lbl_stato.config(text=testo)

    def configura_bindings(self):
        cb = self.canvas_foto
        cb.bind("<Double-Button-1>", self.interazione.gestisci_doppio_click)
        self.root.bind("<Escape>", self.interazione.annulla_zoom)
        cb.bind("<Button-1>", self.interazione.inizia_trascinamento)
        cb.bind("<B1-Motion>", self.interazione.esegui_trascinamento)
        self.root.bind("<Right>", lambda e: self.foto_successiva())
        self.root.bind("<Left>", lambda e: self.foto_precedente())
        cb.bind("<Configure>", self.gestisci_ridimensionamento_finestra)
        self.cmb_filtro.bind("<<ComboboxSelected>>", self.gestisci_cambio_filtro)
        self.cmb_scelta_foto.bind("<<ComboboxSelected>>", self.gestisci_salto_foto_tendina)

    def sincronizza_tendina_file(self):
        if self.collezione.lista_file:
            nomi_brevi = [os.path.basename(f) for f in self.collezione.lista_file]
            self.cmb_scelta_foto.config(values=nomi_brevi, state="readonly")
            if self.collezione.file_attivo:
                nome_corrente = os.path.basename(self.collezione.file_attivo)
                self.cmb_scelta_foto.set(nome_corrente)
        else:
            self.cmb_scelta_foto.config(values=[], state="disabled")
            self.cmb_scelta_foto.set("")
            self.set_status("Nessun file caricato. Apri una cartella NEF per iniziare.")

    def applica_impostazioni_foto_precedente(self):
        if not self.collezione.file_attivo or not self.collezione.lista_file:
            self.set_status("Nessuna foto disponibile per applicare le impostazioni precedenti.")
            return
        c_ind = self.collezione.indice_attivo
        if c_ind <= 0:
            messagebox.showinfo("Informazione", "Ti trovi sulla prima foto dell'elenco.")
            return
        file_precedente = self.collezione.lista_file[c_ind - 1]
        par_precedenti = {}
        if self.collezione.db_manager:
            par_precedenti = self.collezione.db_manager.carica_parametri(file_precedente)
        if not par_precedenti and self.parametri_ultimo_scatto_sviluppato:
            par_precedenti = dict(self.parametri_ultimo_scatto_sviluppato)

        if par_precedenti:
            geometria_corrente = {
                'rotation': self.sld_rotation.get(), 'distortion': self.sld_distortion.get(),
                'crop': self.sld_crop.get(), 'margine': self.sld_margine.get(), 'macchie': list(self.ritocco.macchie)
            }
            par_da_applicare = {
                'brightness': par_precedenti.get('brightness', 1.00), 'contrast': par_precedenti.get('contrast', 1.10),
                'saturation': par_precedenti.get('saturation', 1.05), 'sharpness': par_precedenti.get('sharpness', 150),
                'denoise': par_precedenti.get('denoise', 0.0), 'is_bw': par_precedenti.get('is_bw', False),
                'esportare': self.var_esportare.get(), 'rotation': geometria_corrente['rotation'],
                'distortion': geometria_corrente['distortion'], 'crop': geometria_corrente['crop'],
                'margine': geometria_corrente['margine'], 'macchie': geometria_corrente['macchie']
            }
            self.applica_parametri_a_gui(par_da_applicare)
            self.salva_stato_corrente(); self.aggiorna_anteprima()
            self.set_status(f"Impostazioni caricate dalla foto precedente: {os.path.basename(file_precedente)}")
        else:
            messagebox.showwarning("Attenzione", "Nessun parametro trovato.")
            self.set_status("Nessun parametro precedente disponibile per la foto precedente.")

    def gestisci_salto_foto_tendina(self, event=None):
        indice_scelto = self.cmb_scelta_foto.current()
        if indice_scelto != -1 and self.collezione.lista_file:
            self.salva_stato_corrente(); self.in_zoom = False
            self.interazione_zoom_x = 0; self.interazione_zoom_y = 0
            self.collezione.indice_attivo = indice_scelto
            self.collezione.file_attivo = self.collezione.lista_file[indice_scelto]
            self.carica_immagine_da_stato()

    def foto_prima(self):
        self.salva_stato_corrente(); self.in_zoom = False
        if self.collezione.vai_alla_prima(): self.carica_immagine_da_stato()

    def foto_ultima(self):
        self.salva_stato_corrente(); self.in_zoom = False
        if self.collezione.vai_all_ultima(): self.carica_immagine_da_stato()

    def attiva_strumento_macchie(self):
        if self.in_zoom:
            try:
                x_vis_start, _ = self.canvas_foto.xview()
                y_vis_start, _ = self.canvas_foto.yview()
                scrollregion = self.canvas_foto.cget("scrollregion").split()
                if len(scrollregion) == 4:
                    w_sc = float(scrollregion[2])
                    h_sc = float(scrollregion[3])
                    w_win = self.canvas_foto.winfo_width()
                    h_win = self.canvas_foto.winfo_height()
                    self.zoom_pct_x = (x_vis_start * w_sc + w_win / 2) / self.w_visualizzato
                    self.zoom_pct_y = (y_vis_start * h_sc + h_win / 2) / self.h_visualizzato
            except Exception: pass
        self.ritocco.switch_stato()
        self.btn_macchie.config(text=f"🧹 {'Disattiva' if self.ritocco.attivo else 'Attiva'} Pennello Macchie")
        self.set_status("Pennello macchie attivato" if self.ritocco.attivo else "Pennello macchie disattivato")
        self.aggiorna_anteprima()

    def gestisci_interazione_spunta(self):
        if not self.collezione.file_attivo: return
        self.salva_stato_corrente(); filtro_scelto = self.cmb_filtro.get()
        if filtro_scelto != "Tutti i RAW":
            ind_prec = self.collezione.indice_attivo
            self.collezione.applica_filtro_collezione(filtro_scelto)
            if self.collezione.lista_file:
                nuovo_ind = min(ind_prec, len(self.collezione.lista_file) - 1)
                self.collezione.indice_attivo = nuv_ind = max(0, nuovo_ind)
                self.collezione.file_attivo = self.collezione.lista_file[nuv_ind]
                self.carica_immagine_da_stato()
            else:
                self.collezione.indice_attivo = -1; self.collezione.file_attivo = None
                self.canvas_foto.delete("all"); self.tk_foto = self.img_anteprima_base = None
                self.lbl_info_file.config(text=self.collezione.ottieni_testo_info(), foreground="red")
                self.sincronizza_tendina_file()

    def gestisci_cambio_filtro(self, event=None):
        if not self.collezione.lista_file_completa: return
        self.salva_stato_corrente(); self.in_zoom = False
        filtro_scelto = self.cmb_filtro.get()
        self.collezione.applica_filtro_collezione(filtro_scelto)
        if self.collezione.file_attivo: self.carica_immagine_da_stato()
        else:
            self.canvas_foto.delete("all"); self.tk_foto = self.img_anteprima_base = None
            self.lbl_info_file.config(text=self.collezione.ottieni_testo_info(), foreground="red")
            self.sincronizza_tendina_file()

    def gestisci_ridimensionamento_finestra(self, event):
        if self.img_anteprima_base is None: return
        if self._resize_debounce_id is not None: self.root.after_cancel(self._resize_debounce_id)
        self._resize_debounce_id = self.root.after(200, self._allinea_immagine_anteprima)

    def _allinea_immagine_anteprima(self):
        if not self.tk_foto:
            return
        item_id = self.canvas_foto.find_withtag("immagine_anteprima")
        if not item_id:
            return

        canvas_w = max(1, self.canvas_foto.winfo_width())
        canvas_h = max(1, self.canvas_foto.winfo_height())

        if self.in_zoom:
            self.x_offset_canvas = 0
            self.y_offset_canvas = 0
            self.canvas_foto.coords(item_id, 0, 0)
            return

        x_pos = max(0, (canvas_w - self.w_visualizzato) // 2)
        y_pos = max(0, (canvas_h - self.h_visualizzato) // 2)
        self.x_offset_canvas = x_pos
        self.y_offset_canvas = y_pos
        self.canvas_foto.coords(item_id, x_pos, y_pos)
        self.canvas_foto.config(scrollregion=(0, 0, max(self.w_visualizzato, canvas_w), max(self.h_visualizzato, canvas_h)))

    def raccogli_parametri_attuali(self) -> dict:
        return {
            'brightness': self.sld_brightness.get(), 'contrast': self.sld_contrast.get(),
            'saturation': self.sld_saturation.get(), 'sharpness': self.sld_sharpness.get(),
            'denoise': self.sld_denoise.get(), 'rotation': self.sld_rotation.get(),
            'distortion': self.sld_distortion.get(), 'crop': self.sld_crop.get(),
            'margine': self.sld_margine.get(), 'is_bw': self.var_bw.get(),
            'esportare': self.var_esportare.get(), 'macchie': self.ritocco.macchie
        }

    def applica_parametri_a_gui(self, par: dict):
        self.blocco_salvataggio = True
        self.sld_brightness.set(par.get('brightness', 1.00))
        self.sld_contrast.set(par.get('contrast', 1.10))
        self.sld_saturation.set(par.get('saturation', 1.05))
        self.sld_sharpness.set(par.get('sharpness', 150))
        self.sld_denoise.set(par.get('denoise', 0.0))
        self.sld_rotation.set(par.get('rotation', 0.0))
        self.sld_distortion.set(par.get('distortion', 0.0))
        self.sld_crop.set(par.get('crop', 0.0))
        self.sld_margine.set(par.get('margine', 0.0))
        self.var_bw.set(par.get('is_bw', False))
        self.var_esportare.set(par.get('esportare', True))
        self.ritocco.macchie = par.get('macchie', [])
        self.blocco_salvataggio = False

    def salva_stato_corrente(self):
        if hasattr(self, 'blocco_salvataggio') and self.blocco_salvataggio: return
        c = self.collezione
        if c.file_attivo and c.db_manager:
            attuali = self.raccogli_parametri_attuali()
            c.db_manager.salva_parametri(c.file_attivo, attuali)
            self.parametri_ultimo_scatto_sviluppato = dict(attuali)

    def gestisci_modalita_colore(self):
        if self.collezione.file_attivo:
            self.salva_stato_corrente()
            self.set_status("Cambio modalità colore in corso...")
            self.root.config(cursor="watch"); self.root.update()
            try:
                fz = not self.var_bw.get()
                self.img_anteprima_base = MotoreSviluppo.estrai_immagine_nativa(self.collezione.file_attivo, forza_colore=fz)
                self.aggiorna_anteprima()
            except Exception as e: messagebox.showerror("Errore", str(e))
            finally: self.root.config(cursor="")

    def aggiorna_anteprima(self, event=None):
        if self.img_anteprima_base is None:
            self.set_status("Nessuna immagine da aggiornare.")
            return
        self.set_status("Elaborazione anteprima in corso...")
        self.salva_stato_corrente()
        wc = max(600, self.canvas_foto.winfo_width())
        hc = max(500, self.canvas_foto.winfo_height())
        p = self.raccogli_parametri_attuali()
        z = self.in_zoom
        threading.Thread(target=self._esegui_elaborazione_background, args=(p, wc, hc, z), daemon=True).start()

    def _esegui_elaborazione_background(self, par, wc, hc, in_zoom):
        with self._lock_elaborazione:
            img_el = MotoreSviluppo.applica_editing(
                self.img_anteprima_base, par['brightness'], par['contrast'], 
                par['saturation'], par['sharpness'], par['denoise'],
                par['rotation'], par['distortion'], par['crop'],
                par['margine'], par['macchie'], par['is_bw']
            )
            img_ant = img_el.copy()
            
            molt = 3.0 if in_zoom else 1.0
            img_ant.thumbnail((int(wc * molt), int(hc * molt)), Image.Resampling.BILINEAR)
            
            w_v, h_v = img_ant.width, img_ant.height
            self.root.after(0, self._renderizza_anteprima_gui, img_ant, w_v, h_v)

    def _renderizza_anteprima_gui(self, img_ant, w_v, h_v):

        self.w_visualizzato, self.h_visualizzato = w_v, h_v
        self.canvas_foto.unbind("<Configure>")
        for elem in self.canvas_foto.find_all():
            if elem != self.ritocco.id_cursore_mobile: self.canvas_foto.delete(elem)

        canvas_w = max(1, self.canvas_foto.winfo_width())
        canvas_h = max(1, self.canvas_foto.winfo_height())
        self.canvas_foto.config(scrollregion=(0, 0, max(w_v, canvas_w), max(h_v, canvas_h)))
        self.tk_foto = ImageTk.PhotoImage(img_ant)

        if self.in_zoom:
            self.x_offset_canvas = 0
            self.y_offset_canvas = 0
            self.canvas_foto.create_image(0, 0, image=self.tk_foto, anchor=tk.NW, tags="immagine_anteprima")
            self.root.after(10, self._esegui_centratura_post_render)
        else:
            x_pos = max(0, (canvas_w - w_v) // 2)
            y_pos = max(0, (canvas_h - h_v) // 2)
            self.x_offset_canvas = x_pos
            self.y_offset_canvas = y_pos
            self.canvas_foto.create_image(x_pos, y_pos, image=self.tk_foto, anchor=tk.NW, tags="immagine_anteprima")
            self.set_status("Anteprima aggiornata")

        self._allinea_immagine_anteprima()
        self.disegna_indicatori_macchie()
        self.canvas_foto.bind("<Configure>", self.gestisci_ridimensionamento_finestra)

    def _esegui_centratura_post_render(self):
        w_win = max(1, self.canvas_foto.winfo_width())
        h_win = max(1, self.canvas_foto.winfo_height())
        pixel_x = (self.zoom_pct_x * self.w_visualizzato)
        pixel_y = (self.zoom_pct_y * self.h_visualizzato)
        target_x = pixel_x - (w_win / 2)
        target_y = pixel_y - (h_win / 2)
        scrollregion = self.canvas_foto.cget("scrollregion").split()
        if len(scrollregion) == 4:
            totale_w = float(scrollregion[2])
            totale_h = float(scrollregion[3])
            moveto_x = max(0.0, min(1.0, target_x / totale_w)) if totale_w > 0 else 0.0
            moveto_y = max(0.0, min(1.0, target_y / totale_h)) if totale_h > 0 else 0.0
            self.canvas_foto.xview_moveto(moveto_x)
            self.canvas_foto.yview_moveto(moveto_y)


    def disegna_indicatorie_macchie(self): self.disegna_indicatori_macchie()

    def disegna_indicatori_macchie(self):
        for elemento in self.canvas_foto.find_withtag("indicatore_cerchio"): self.canvas_foto.delete(elemento)
        for elemento in self.canvas_foto.find_withtag("badge_overlay"): self.canvas_foto.delete(elemento)

        if self.ritocco.attivo:
            msg = f"🧹 PENNELLO MACCHIE (Raggio: {int(self.ritocco.raggio_pennello)}px) | Ctrl+Z: Annulla | B: Disattiva"
            self.canvas_foto.create_rectangle(12, 12, 540, 38, fill="#2b0000", outline="#ff4444", width=1, tags="badge_overlay")
            self.canvas_foto.create_text(20, 25, text=msg, fill="#ff8888", anchor=tk.W, font=("Segoe UI", 9, "bold"), tags="badge_overlay")
        elif self.in_zoom:
            msg = "🔍 ZOOM 100% ATTIVO - ESC o Doppio Click per Annullare"
            self.canvas_foto.create_rectangle(12, 12, 380, 38, fill="#001b2e", outline="#00aaff", width=1, tags="badge_overlay")
            self.canvas_foto.create_text(20, 25, text=msg, fill="#66ccff", anchor=tk.W, font=("Segoe UI", 9, "bold"), tags="badge_overlay")

        if not self.img_anteprima_base or not self.ritocco.attivo: return
        w_orig, h_orig = self.img_anteprima_base.size
        for macchia in self.ritocco.macchie:
            if len(macchia) == 5:
                mx, my, sx, sy, raggio = macchia
            elif len(macchia) == 3:
                mx, my, raggio = macchia
                sx = max(0, mx - raggio * 2)
                sy = my
            else:
                continue

            rx, ry = self.ritocco.native_to_screen_coords(mx, my)
            rsx, rsy = self.ritocco.native_to_screen_coords(sx, sy)
            params = self.ritocco._ottieni_parametri_trasformazione()
            scale = params['scale_x'] if params is not None else (self.w_visualizzato / w_orig)
            rad_vis = max(4, raggio * scale)

            self.canvas_foto.create_oval(rx - rad_vis, ry - rad_vis, rx + rad_vis, ry + rad_vis, outline="#ff3333", width=2, tags="indicatore_cerchio")
            self.canvas_foto.create_oval(rsx - rad_vis, rsy - rad_vis, rsx + rad_vis, rsy + rad_vis, outline="#00bfff", width=1, tags="indicatore_cerchio")
            self.canvas_foto.create_line(rx, ry, rsx, rsy, fill="#aaaaaa", dash=(2, 2), tags="indicatore_cerchio")


    def _renderizza_lightbox(self):
        if not hasattr(self, 'lightbox_window') or not self.lightbox_window.winfo_exists():
            return
        if not hasattr(self, 'lightbox_canvas') or self.lightbox_canvas is None:
            return
        if self.img_anteprima_base is None:
            return

        self.lightbox_window.update_idletasks()
        p = self.raccogli_parametri_attuali()
        img_el = MotoreSviluppo.applica_editing(
            self.img_anteprima_base, p['brightness'], p['contrast'],
            p['saturation'], p['sharpness'], p['denoise'],
            p['rotation'], p['distortion'], p['crop'],
            p['margine'], p['macchie'], p['is_bw']
        )
        img_full = img_el.copy()
        self.lightbox_canvas.delete("all")

        zoom_attivo = getattr(self, 'lightbox_zoom_active', False)
        canvas_w = max(1, self.lightbox_canvas.winfo_width())
        canvas_h = max(1, self.lightbox_canvas.winfo_height())

        if not zoom_attivo:
            win_w = max(1, self.lightbox_window.winfo_width() - 20)
            win_h = max(1, self.lightbox_window.winfo_height() - 20)
            img_display = img_full.copy()
            img_display.thumbnail((win_w, win_h), Image.Resampling.BILINEAR)
            self.lightbox_display_width = img_display.width
            self.lightbox_display_height = img_display.height
            self.lightbox_photo = ImageTk.PhotoImage(img_display)
            x_pos, y_pos, scrollregion = calcola_layout_lightbox(
                canvas_w=canvas_w,
                canvas_h=canvas_h,
                img_w=img_display.width,
                img_h=img_display.height,
                zoom_attivo=False,
            )
            self.lightbox_canvas.config(scrollregion=scrollregion)
            self.lightbox_image_offset_x = x_pos
            self.lightbox_image_offset_y = y_pos
            self.lightbox_canvas.create_image(x_pos, y_pos, image=self.lightbox_photo, anchor=tk.NW, tags="lightbox_img")
        else:
            self.lightbox_photo = ImageTk.PhotoImage(img_full)
            focus_x = getattr(self, 'lightbox_focus_x', 0.5)
            focus_y = getattr(self, 'lightbox_focus_y', 0.5)
            x_pos, y_pos, scrollregion = calcola_layout_lightbox(
                canvas_w=canvas_w,
                canvas_h=canvas_h,
                img_w=img_full.width,
                img_h=img_full.height,
                focus_x=focus_x,
                focus_y=focus_y,
                zoom_attivo=True,
            )
            self.lightbox_canvas.config(scrollregion=scrollregion)
            self.lightbox_image_offset_x = x_pos
            self.lightbox_image_offset_y = y_pos
            self.lightbox_canvas.create_image(x_pos, y_pos, image=self.lightbox_photo, anchor=tk.NW, tags="lightbox_img")

    def _inizia_trascinamento_lightbox(self, event):
        if not getattr(self, 'lightbox_zoom_active', False):
            return
        self.lightbox_canvas.scan_mark(event.x, event.y)

    def _trascina_lightbox(self, event):
        if not getattr(self, 'lightbox_zoom_active', False):
            return
        self.lightbox_canvas.scan_dragto(event.x, event.y, gain=1)

    def gestisci_doppio_click_lightbox(self, event=None):
        if self.img_anteprima_base is None:
            return
        if event is not None:
            canvas_x = self.lightbox_canvas.canvasx(event.x)
            canvas_y = self.lightbox_canvas.canvasy(event.y)
            disp_w = getattr(self, 'lightbox_display_width', 1)
            disp_h = getattr(self, 'lightbox_display_height', 1)
            if disp_w > 0 and disp_h > 0:
                self.lightbox_focus_x = max(0.0, min(1.0, (canvas_x - self.lightbox_image_offset_x) / disp_w))
                self.lightbox_focus_y = max(0.0, min(1.0, (canvas_y - self.lightbox_image_offset_y) / disp_h))
        self.lightbox_zoom_active = not getattr(self, 'lightbox_zoom_active', False)
        self._renderizza_lightbox()

    def apri_lightbox(self):
        """Mostra un overlay full-screen con l'anteprima corrente.

        L'overlay viene chiuso premendo `Esc` o cliccando su qualsiasi punto.
        Se già aperto, porta la finestra in primo piano.
        """
        if not self.img_anteprima_base:
            self.set_status("Nessuna immagine disponibile per la lightbox.")
            return

        if hasattr(self, 'lightbox_window') and self.lightbox_window.winfo_exists():
            self._renderizza_lightbox()
            self.lightbox_window.lift()
            return

        self.lightbox_zoom_active = False
        self.lightbox_window = tk.Toplevel(self.root)
        self.lightbox_window.title("Anteprima Lightbox")
        self.lightbox_window.configure(background="black")
        self.lightbox_window.attributes("-topmost", True)
        self.lightbox_window.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.lightbox_window.bind("<Escape>", lambda event: self.lightbox_window.destroy())
        self.lightbox_window.bind("<Configure>", lambda event: self._renderizza_lightbox())
        self.lightbox_window.transient(self.root)
        self.lightbox_window.grab_set()

        self.lightbox_canvas = tk.Canvas(self.lightbox_window, bg="black", highlightthickness=0)
        self.lightbox_canvas.pack(fill=tk.BOTH, expand=True)
        self.lightbox_canvas.bind("<Double-Button-1>", self.gestisci_doppio_click_lightbox)
        self.lightbox_canvas.bind("<Button-1>", self._inizia_trascinamento_lightbox)
        self.lightbox_canvas.bind("<B1-Motion>", self._trascina_lightbox)
        self._renderizza_lightbox()
        self.set_status("Lightbox aperta. Premi Esc o clicca per chiudere. Double click per zoom, drag per spostare la vista.")

    def apri_dialog_esportazione_singola(self):
        if not self.collezione.file_attivo: return
        self.salva_stato_corrente()
        DialogEsportazione(self.root, self.collezione.file_attivo, self.raccogli_parametri_attuali())

    def esegui_batch_completo(self):
        if not self.collezione.lista_file: return
        self.salva_stato_corrente()
        cartella_dest = filedialog.askdirectory(title="Seleziona cartella Batch")
        if not cartella_dest: return
        self.root.config(cursor="watch"); self.root.update()
        try:
            esportatore = EsportatoreCanali(self.collezione.db_manager)
            suc, tot = esportatore.esegui_processo_batch(self.collezione.lista_file, cartella_dest)
            messagebox.showinfo("Batch Terminato", f"Salvate con successo {suc} su {tot} foto.")
        except Exception as e: messagebox.showerror("Errore Batch", f"Si è verificato un problema:\n{str(e)}")
        finally: self.root.config(cursor="")

    def gestisci_chiusura_app(self):
        try: self.salva_stato_corrente()
        except Exception: pass
        if self.collezione.db_manager: self.collezione.db_manager.chiudi()
        self.root.destroy()

    def carica_cartella_raw(self):
        cartella = filedialog.askdirectory()
        if cartella and self.collezione.inizializza_cartella(cartella):
            self.btn_first.config(state=tk.NORMAL); self.btn_prev.config(state=tk.NORMAL)
            self.btn_next.config(state=tk.NORMAL); self.btn_last.config(state=tk.NORMAL)
            self.btn_copia_prec.config(state=tk.NORMAL)
            self.cmb_filtro.set("Tutti i RAW")
            self.carica_immagine_da_stato()

    def carica_immagine_da_stato(self):
        c = self.collezione
        if c.file_attivo:
            self.ritocco.disattiva()
            self.btn_macchie.config(text="🧹 Attiva Pennello Macchie")
            self.canvas_foto.delete("all")
            self.tk_foto = self.img_anteprima_base = None
            self.in_zoom = False
            self.interazione_zoom_x = 0; self.interazione_zoom_y = 0
            self.lbl_info_file.config(text=c.ottieni_testo_info(), foreground="black")
            par = c.db_manager.carica_parametri(c.file_attivo)
            self.applica_parametri_a_gui(par if par else {})
            self.root.update_idletasks()
            self.sincronizza_tendina_file()
            try:
                fz = not self.var_bw.get()
                self.img_anteprima_base = MotoreSviluppo.estrai_immagine_nativa(c.file_attivo, forza_colore=fz)
                self.set_status(f"Modalità colore cambiata: {'B/N' if self.var_bw.get() else 'Colore'}")
                self.aggiorna_anteprima()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
                self.set_status(f"Errore nell'apertura immagine: {str(e)}")

    def foto_successiva(self):
        self.salva_stato_corrente(); self.in_zoom = False
        if self.collezione.avanti(): self.carica_immagine_da_stato()

    def foto_precedente(self):
        self.salva_stato_corrente(); self.in_zoom = False
        if self.collezione.indietro(): self.carica_immagine_da_stato()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppSviluppoRaw(root)
    root.mainloop()
