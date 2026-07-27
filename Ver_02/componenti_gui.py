"""Componenti UI riusabili per l'applicazione.

Contiene widget helper e la fabbrica di layout ``ComponentiGui`` usata da
``app_gui.AppSviluppoRaw`` per costruire l'interfaccia utente.

Note
----
Le funzioni qui esposte sono utili a separare la logica di layout dalla
logica di controllo dell'applicazione, consentendo un semplice testing
dei singoli pannelli.

    .. rubric:: Esempio

    .. code-block:: python

        ComponentiGui.crea_layout(self)
        ComponentiGui.crea_menu(self)
        ComponentiGui.crea_controlli(self)

"""

import tkinter as tk
from tkinter import ttk, messagebox

class ToolTip:
    """Tooltip semplice per i widget Tkinter."""

    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide)
        widget.bind("<ButtonPress>", self.hide)

    def schedule(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self):
        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 2
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#2d2d30", foreground="#ffffff",
                         relief=tk.SOLID, borderwidth=1, font=("Segoe UI", 9))
        label.pack(ipadx=6, ipady=3)

    def hide(self, event=None):
        self.unschedule()
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class ComponentiGui:
    """Gestore del layout visivo scorrevole organizzato in LabelFrame."""

    @staticmethod
    def applica_tema_scuro(app):
        """Configura uno stile Darkroom professionale ed elegante per tutti i widget TTK."""
        BG_MAIN = "#1e1e1e"
        BG_PANEL = "#252526"
        BG_WIDGET = "#333337"
        BG_ACTIVE = "#007acc"
        FG_TEXT = "#e1e1e1"
        BORDER_COL = "#3e3e42"

        app.root.configure(bg=BG_MAIN)
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure(".", background=BG_PANEL, foreground=FG_TEXT, font=("Segoe UI", 10))
        style.configure("TFrame", background=BG_PANEL)
        style.configure("TLabel", background=BG_PANEL, foreground=FG_TEXT)

        style.configure("TButton", background=BG_WIDGET, foreground="#ffffff", bordercolor=BORDER_COL, borderwidth=1, focuscolor="none", padding=(5, 3))
        style.map("TButton",
                  background=[("active", BG_ACTIVE), ("disabled", "#222225")],
                  foreground=[("disabled", "#555555")],
                  bordercolor=[("active", BG_ACTIVE)])

        style.configure("TCheckbutton", background=BG_PANEL, foreground=FG_TEXT)
        style.map("TCheckbutton",
                  background=[("active", BG_PANEL)],
                  foreground=[("active", "#ffffff")])

        style.configure("TCombobox", fieldbackground=BG_MAIN, background=BG_WIDGET, foreground="#ffffff", arrowcolor="#ffffff", bordercolor=BORDER_COL)
        style.map("TCombobox",
                  fieldbackground=[("readonly", BG_MAIN)],
                  foreground=[("readonly", "#ffffff")])

        style.configure("TScale", background=BG_PANEL, troughcolor=BG_MAIN, sliderlength=14, borderwidth=0)
        style.map("TScale", background=[("active", BG_PANEL)])

        style.configure("Vertical.TScrollbar", background=BG_WIDGET, troughcolor=BG_MAIN, bordercolor=BG_MAIN, arrowcolor="#cccccc")
        style.map("Vertical.TScrollbar", background=[("active", BG_ACTIVE)])

    @staticmethod
    def crea_layout(app):
        """Crea un pannello sinistro interamente scorrevole tramite scrollbar in stile Dark Mode."""
        ComponentiGui.applica_tema_scuro(app)

        app.root.option_add("*Font", "{Segoe UI} 10")
        app.root.minsize(1100, 720)
        app.root.columnconfigure(0, weight=0, minsize=380)
        app.root.columnconfigure(1, weight=1)
        app.root.rowconfigure(0, weight=1)
        app.root.rowconfigure(1, weight=0)

        # Contenitore principale sinistro
        app.pan_sinistro_root = ttk.Frame(app.root)
        app.pan_sinistro_root.grid(row=0, column=0, sticky="nsew")
        app.pan_sinistro_root.rowconfigure(0, weight=1)
        app.pan_sinistro_root.columnconfigure(0, weight=1)

        # Canvas interno con sfondo scuro e Scrollbar per il pannello controlli
        canvas_scroll = tk.Canvas(app.pan_sinistro_root, bg="#252526", borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(app.pan_sinistro_root, orient="vertical", command=canvas_scroll.yview)
        
        app.canvas_controlli = canvas_scroll
        
        # Frame effettivo che conterrà i widget inserito nel canvas
        app.pan_sinistro = ttk.Frame(canvas_scroll, padding=(8, 2, 8, 8))
        
        # Configurazione del meccanismo di scorrimento della pagina
        app.pan_sinistro.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        id_finestra = canvas_scroll.create_window((0, 0), window=app.pan_sinistro, anchor="nw")
        
        # Fa in modo che the frame interno si allarghi quanto il canvas
        canvas_scroll.bind('<Configure>', lambda e: canvas_scroll.itemconfig(id_finestra, width=e.width))
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        # Posizionamento dei componenti di scorrimento nella griglia
        canvas_scroll.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Permette di usare la rotella del mouse per scorrere i controlli
        def _sul_mouse_wheel(event):
            canvas_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas_scroll.bind_all("<MouseWheel>", _sul_mouse_wheel)

        # Pannello destro (Canvas per la Immagine RAW)
        app.pan_destro = ttk.Frame(app.root, padding="5")
        app.pan_destro.grid(row=0, column=1, sticky="nsew")
        app.pan_destro.columnconfigure(0, weight=1)
        app.pan_destro.rowconfigure(0, weight=1)

        app.canvas_foto = tk.Canvas(app.pan_destro, bg="#1e1e1e", highlightthickness=0)
        app.canvas_foto.grid(row=0, column=0, sticky="nsew")
        app._debounce_id = None

        # Barra di stato nella parte inferiore
        app.status_bar = ttk.Frame(app.root, padding=(8, 4))
        app.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        app.lbl_stato = ttk.Label(app.status_bar, text="Pronto", anchor=tk.W, foreground="#aaaaaa")
        app.lbl_stato.pack(fill=tk.X)


    @staticmethod
    def crea_menu(app):
        menubar = tk.Menu(app.root)
        app.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Apri Cartella RAW...", accelerator="Ctrl+O", command=app.carica_cartella_raw)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", accelerator="Ctrl+Q", command=app.gestisci_chiusura_app)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Annulla Ultima Macchia", accelerator="Ctrl+Z", command=lambda: app.ritocco.annulla_ultima_macchia())
        edit_menu.add_command(label="Attiva/Disattiva Pennello Macchie", accelerator="B", command=app.attiva_strumento_macchie)
        menubar.add_cascade(label="Modifica", menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Reset Vista / Annulla Zoom", accelerator="Esc", command=app.interazione.annulla_zoom)
        view_menu.add_command(label="Lightbox", accelerator="Ctrl+L", command=app.apri_lightbox)
        menubar.add_cascade(label="Vista", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Guida Rapida", command=lambda: app.set_status("Doppio click: zoom | Esc: torna normale | Pennello (B): correggi macchie | Ctrl+Z: annulla macchia."))
        help_menu.add_separator()
        help_menu.add_command(label="Informazioni", command=lambda: messagebox.showinfo("Informazioni", "Nikon NEF Batch Editor - Ver_02\nInterfaccia di sviluppo RAW e ritocco."))
        menubar.add_cascade(label="Aiuto", menu=help_menu)

        app.root.bind_all("<Control-o>", lambda event: app.carica_cartella_raw())
        app.root.bind_all("<Control-O>", lambda event: app.carica_cartella_raw())
        app.root.bind_all("<Control-q>", lambda event: app.gestisci_chiusura_app())
        app.root.bind_all("<Control-Q>", lambda event: app.gestisci_chiusura_app())
        app.root.bind_all("<Control-l>", lambda event: app.apri_lightbox())
        app.root.bind_all("<Control-L>", lambda event: app.apri_lightbox())
        app.root.bind_all("<Control-z>", lambda event: app.ritocco.annulla_ultima_macchia())
        app.root.bind_all("<Control-Z>", lambda event: app.ritocco.annulla_ultima_macchia())
        app.root.bind_all("<b>", lambda event: app.attiva_strumento_macchie())
        app.root.bind_all("<B>", lambda event: app.attiva_strumento_macchie())
        app.root.bind_all("<Escape>", lambda event: app.interazione.annulla_zoom())

    @staticmethod
    def crea_tooltip(widget, text):
        if widget is not None:
            ToolTip(widget, text)

    @staticmethod
    def pianifica_aggiornamento_ottimizzato(app, *args):
        if hasattr(app, '_debounce_id') and app._debounce_id is not None:
            app.root.after_cancel(app._debounce_id)
        app._debounce_id = app.root.after(150, app.aggiorna_anteprima)

    @staticmethod
    def crea_sezione_collassabile(parent, titolo, builder, espansa=True):
        """Crea una sezione con intestazione cliccabile e contenuto espandibile."""
        outer = ttk.Frame(parent, padding=(0, 0, 0, 4))
        outer.pack(fill=tk.X, pady=(2, 4))

        header = ttk.Frame(outer)
        header.pack(fill=tk.X)

        expanded = {"value": espansa}

        def toggle_section():
            if expanded["value"]:
                content.pack_forget()
                btn_toggle.configure(text="▶")
                expanded["value"] = False
            else:
                content.pack(fill=tk.X)
                btn_toggle.configure(text="▼")
                expanded["value"] = True

        btn_toggle = ttk.Button(header, text="▼" if espansa else "▶", width=2, command=toggle_section)
        btn_toggle.pack(side=tk.LEFT)

        lbl_titolo = ttk.Label(header, text=titolo, font=("Segoe UI", 10, "bold"), cursor="hand2")
        lbl_titolo.pack(side=tk.LEFT, padx=(6, 0))
        lbl_titolo.bind("<Button-1>", lambda e: toggle_section())

        content = ttk.Frame(outer, padding=(4, 4, 0, 0))
        if espansa:
            content.pack(fill=tk.X)
        else:
            content.pack_forget()

        builder(content)
        return outer

    @staticmethod
    def crea_controlli(app):
        """Genera i widget divisi in sezioni collassabili ordinate."""

        def aggiungi_slider(contenitore, label, min_v, max_v, def_v, fmt="{:.1f}"):
            frame_lbl = ttk.Frame(contenitore)
            frame_lbl.pack(fill=tk.X, pady=(3, 0))
            
            lbl_title = ttk.Label(frame_lbl, text=label, cursor="hand2")
            lbl_title.pack(side=tk.LEFT)

            frame_slider = ttk.Frame(contenitore)
            frame_slider.pack(fill=tk.X, pady=(0, 3))

            sld = ttk.Scale(frame_slider, from_=min_v, to=max_v, value=def_v)
            sld.pack(side=tk.LEFT, fill=tk.X, expand=True)

            valore_var = tk.StringVar(value=fmt.format(def_v))
            ttk.Label(frame_slider, textvariable=valore_var, width=6, anchor=tk.E).pack(side=tk.LEFT, padx=(4, 2))

            def reset_valore():
                sld.set(def_v)
                valore_var.set(fmt.format(def_v))
                ComponentiGui.pianifica_aggiornamento_ottimizzato(app)

            lbl_title.bind("<Double-Button-1>", lambda e: reset_valore())
            ComponentiGui.crea_tooltip(lbl_title, f"Doppio click per resettare a {fmt.format(def_v)}")

            btn_reset = ttk.Button(frame_slider, text="↺", width=2, command=reset_valore)
            btn_reset.pack(side=tk.LEFT, padx=(2, 0))
            ComponentiGui.crea_tooltip(btn_reset, f"Ripristina valore predefinito ({fmt.format(def_v)})")

            def on_slider_change(v):
                valore_var.set(fmt.format(float(v)))
                ComponentiGui.pianifica_aggiornamento_ottimizzato(app)

            sld.configure(command=on_slider_change)
            return sld

        # --- SEZIONE 1: FILTRO E NAVIGAZIONE --- (Aperta)
        ComponentiGui.crea_sezione_collassabile(
            app.pan_sinistro,
            "🔍 Filtra Visualizzazione",
            lambda sec_file: [
                ttk.Label(sec_file, text="Stato Filtro:").pack(anchor=tk.W, pady=(2, 0)),
                setattr(app, 'cmb_filtro', ttk.Combobox(sec_file, state="readonly", values=["Tutti i RAW", "Solo selezionati", "Solo NON selezionati"])),
                app.cmb_filtro.set("Tutti i RAW"),
                app.cmb_filtro.pack(fill=tk.X, pady=(0, 4)),
                ttk.Label(sec_file, text="🎯 Vai alla foto:").pack(anchor=tk.W, pady=(4, 0)),
                setattr(app, 'cmb_scelta_foto', ttk.Combobox(sec_file, state="readonly")),
                app.cmb_scelta_foto.pack(fill=tk.X, pady=(0, 4)),
                setattr(app, 'lbl_info_file', ttk.Label(sec_file, text="Nessun file caricato", wraplength=280, justify=tk.LEFT)),
                app.lbl_info_file.pack(fill=tk.X, pady=4),
                (lambda: (setattr(app, 'btn_first', ttk.Button(sec_file, text="⏮", width=4, state=tk.DISABLED, command=app.foto_prima)),
                          setattr(app, 'btn_prev', ttk.Button(sec_file, text="◀ Prec.", state=tk.DISABLED, command=app.foto_precedente)),
                          setattr(app, 'btn_next', ttk.Button(sec_file, text="Succ. ▶", state=tk.DISABLED, command=app.foto_successiva)),
                          setattr(app, 'btn_last', ttk.Button(sec_file, text="⏭", width=4, state=tk.DISABLED, command=app.foto_ultima)),
                          None))(),
                frame_nav := (lambda: (lambda frame_nav: frame_nav)(ttk.Frame(sec_file)))(),
                app.btn_first.pack(side=tk.LEFT, padx=(0, 2)),
                app.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2),
                app.btn_next.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2),
                app.btn_last.pack(side=tk.LEFT, padx=(2, 0)),
            ][-1],
            espansa=True,
        )

        # --- SEZIONE 2: SVILUPPO E COLORE --- (Aperta)
        ComponentiGui.crea_sezione_collassabile(
            app.pan_sinistro,
            "🎨 Sviluppo e Colore",
            lambda sec_colore: [
                setattr(app, 'btn_copia_prec', ttk.Button(sec_colore, text="📋 Applica Impostazioni Precedente", state=tk.DISABLED, command=app.applica_impostazioni_foto_precedente)),
                app.btn_copia_prec.pack(fill=tk.X, pady=(0, 6)),
                ComponentiGui.crea_tooltip(app.btn_copia_prec, "Applica i parametri salvati dalla foto precedente."),
                setattr(app, 'sld_brightness', aggiungi_slider(sec_colore, "Luminosità", 0.5, 2.0, 1.0)),
                setattr(app, 'sld_contrast', aggiungi_slider(sec_colore, "Contrasto", 0.5, 2.0, 1.0)),
                setattr(app, 'sld_saturation', aggiungi_slider(sec_colore, "Saturazione", 0.0, 2.0, 1.0)),
                setattr(app, 'sld_sharpness', aggiungi_slider(sec_colore, "Nitidezza (Sharpness)", 100, 300, 100, fmt="{:.0f}")),
                setattr(app, 'sld_denoise', aggiungi_slider(sec_colore, "Riduzione Disturbo (Denoise)", 0.0, 5.0, 0.0)),
                setattr(app, 'var_bw', tk.BooleanVar(value=False)),
                ttk.Checkbutton(sec_colore, text="Converti in Bianco e Nero", variable=app.var_bw, command=app.gestisci_modalita_colore).pack(fill=tk.X, pady=4),
            ][-1],
            espansa=True,
        )

        # --- SEZIONE 3: GEOMETRIA E RITAGLIO --- (Chiusa)
        ComponentiGui.crea_sezione_collassabile(
            app.pan_sinistro,
            "📐 Geometria e Ritaglio",
            lambda sec_geom: [
                setattr(app, 'sld_rotation', aggiungi_slider(sec_geom, "Rotazione Angolo (°)", -45.0, 45.0, 0.0)),
                setattr(app, 'sld_distortion', aggiungi_slider(sec_geom, "Distorsione Lente", -5.0, 5.0, 0.0)),
                setattr(app, 'sld_crop', aggiungi_slider(sec_geom, "Ritaglio Orizzontale (Crop %)", 0.0, 40.0, 0.0)),
                setattr(app, 'sld_margine', aggiungi_slider(sec_geom, "Ritaglio Verticale (Margine %)", 0.0, 40.0, 0.0)),
            ][-1],
            espansa=False,
        )

        # --- SEZIONE 4: AZIONI DI OUTPUT --- (Chiusa)
        ComponentiGui.crea_sezione_collassabile(
            app.pan_sinistro,
            "⚙️ Azioni di Output",
            lambda sec_azione: [
                setattr(app, 'btn_macchie', ttk.Button(sec_azione, text="🧹 Attiva Pennello Macchie (B)", command=app.attiva_strumento_macchie)),
                app.btn_macchie.pack(fill=tk.X, pady=3),
                ComponentiGui.crea_tooltip(app.btn_macchie, "Attiva/disattiva lo strumento penna per ritocco macchie (Scorciatoia: B). Ctrl+Z per annullare."),
                setattr(app, 'btn_lightbox', ttk.Button(sec_azione, text="🖼️ Anteprima Lightbox (Ctrl+L)", command=app.apri_lightbox)),
                app.btn_lightbox.pack(fill=tk.X, pady=3),
                ComponentiGui.crea_tooltip(app.btn_lightbox, "Apri un overlay di anteprima a schermo intero dell'immagine corrente."),
                ttk.Button(sec_azione, text="🔄 Reset Vista / Annulla Zoom (Esc)", command=app.interazione.annulla_zoom).pack(fill=tk.X, pady=3),
                setattr(app, 'var_esportare', tk.BooleanVar(value=True)),
                (lambda: (chk_batch := ttk.Checkbutton(sec_azione, text="Seleziona Foto per Batch", variable=app.var_esportare, command=app.gestisci_interazione_spunta), chk_batch.pack(fill=tk.X, pady=4), ComponentiGui.crea_tooltip(chk_batch, "Marca o demarca la foto corrente per le operazioni batch."), chk_batch))(),
                (lambda: (btn_salva := ttk.Button(sec_azione, text="💾 Salva Foto Corrente...", command=app.apri_dialog_esportazione_singola), btn_salva.pack(fill=tk.X, pady=3), ComponentiGui.crea_tooltip(btn_salva, "Salva l'immagine corrente con i parametri selezionati."), btn_salva))(),
                (lambda: (btn_batch := ttk.Button(sec_azione, text="🚀 AVVIA BATCH SULLE SELEZIONATE", command=app.esegui_batch_completo), btn_batch.pack(fill=tk.X, pady=3), ComponentiGui.crea_tooltip(btn_batch, "Esegui l'elaborazione batch sulle foto selezionate."), btn_batch))(),
            ][-1],
            espansa=False,
        )

        # --- SEZIONE 5: GUIDA RAPIDA --- (Chiusa)
        ComponentiGui.crea_sezione_collassabile(
            app.pan_sinistro,
            "🛈 Guida Rapida & Scorciatoie",
            lambda sec_help: ttk.Label(sec_help, text="• Doppio click: Zoom 100% / Reset\n• Drag sul Canvas: Sposta vista zoomata\n• Tastiera ◄ / ►: Foto prec / succ\n• B: Attiva/Disattiva Pennello macchie\n• Ctrl+Z: Annulla ultima macchia\n• ↺ o Doppio Click sullo Slider: Reset valore", wraplength=300, justify=tk.LEFT).pack(fill=tk.X),
            espansa=False,
        )


