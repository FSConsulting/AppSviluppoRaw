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
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0",
                         relief=tk.SOLID, borderwidth=1, font=("Segoe UI", 9))
        label.pack(ipadx=4, ipady=2)

    def hide(self, event=None):
        self.unschedule()
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class ComponentiGui:
    """Gestore del layout visivo scorrevole organizzato in LabelFrame."""

    @staticmethod
    def crea_layout(app):
        """Crea un pannello sinistro interamente scorrevole tramite scrollbar."""
        app.root.option_add("*Font", "{Segoe UI} 10")
        app.root.minsize(1100, 720)
        app.root.columnconfigure(0, weight=0, minsize=380)
        app.root.columnconfigure(1, weight=1)
        app.root.rowconfigure(0, weight=1)
        app.root.rowconfigure(1, weight=0)

        # Contenitore principale sinistro
        app.pan_sinistro_root = ttk.Frame(app.root, relief=tk.SUNKEN)
        app.pan_sinistro_root.grid(row=0, column=0, sticky="nsew")
        app.pan_sinistro_root.rowconfigure(0, weight=1)
        app.pan_sinistro_root.columnconfigure(0, weight=1)

        # Canvas interno e Scrollbar per il pannello controlli
        canvas_scroll = tk.Canvas(app.pan_sinistro_root, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(app.pan_sinistro_root, orient="vertical", command=canvas_scroll.yview)
        
        app.canvas_controlli = canvas_scroll
        
        # Frame effettivo che conterrà i widget inserito nel canvas
        app.pan_sinistro = ttk.Frame(canvas_scroll, padding="10")
        
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

        app.canvas_foto = tk.Canvas(app.pan_destro, bg="#252525", highlightthickness=0)
        app.canvas_foto.grid(row=0, column=0, sticky="nsew")
        app._debounce_id = None

        # Barra di stato nella parte inferiore
        app.status_bar = ttk.Frame(app.root, relief=tk.SUNKEN, padding=(5, 2))
        app.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        app.lbl_stato = ttk.Label(app.status_bar, text="Pronto", anchor=tk.W)
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

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Reset Vista / Annulla Zoom", accelerator="Esc", command=app.interazione.annulla_zoom)
        view_menu.add_command(label="Lightbox", accelerator="Ctrl+L", command=app.apri_lightbox)
        menubar.add_cascade(label="Vista", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Guida Rapida", command=lambda: app.set_status("Doppio click: zoom | Esc: torna normale | Pennello macchie: correggi difetti."))
        help_menu.add_separator()
        help_menu.add_command(label="Informazioni", command=lambda: messagebox.showinfo("Informazioni", "Nikon NEF Batch Editor - Ver_02\nInterfaccia di sviluppo RAW e ritocco."))
        menubar.add_cascade(label="Aiuto", menu=help_menu)

        app.root.bind_all("<Control-o>", lambda event: app.carica_cartella_raw())
        app.root.bind_all("<Control-q>", lambda event: app.gestisci_chiusura_app())
        app.root.bind_all("<Control-l>", lambda event: app.apri_lightbox())
        app.root.bind_all("<Escape>", lambda event: app.annulla_zoom())

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
    def crea_controlli(app):
        """Genera i widget divisi in sezioni LabelFrame ordinate."""
        
        # --- SEZIONE 1: GESTIONE E NAVIGAZIONE FILE ---
        sec_file = ttk.LabelFrame(app.pan_sinistro, text=" 🗂️ Gestione File e Navigazione ", padding="8")
        sec_file.pack(fill=tk.X, pady=5)

        ttk.Button(sec_file, text="📁 Apri Cartella RAW NEF...", command=app.carica_cartella_raw).pack(fill=tk.X, pady=4)
        
        ttk.Label(sec_file, text="🔍 Filtra Visualizzazione:").pack(anchor=tk.W, pady=(4, 0))
        app.cmb_filtro = ttk.Combobox(sec_file, state="readonly", 
                                      values=["Tutti i RAW", "Solo selezionati", "Solo NON selezionati"])
        app.cmb_filtro.set("Tutti i RAW")
        app.cmb_filtro.pack(fill=tk.X, pady=(0, 4))
        
        app.lbl_info_file = ttk.Label(sec_file, text="Nessun file caricato", wraplength=280, justify=tk.LEFT)
        app.lbl_info_file.pack(fill=tk.X, pady=6)

        # Riga con 4 pulsanti di navigazione affiancati
        frame_nav = ttk.Frame(sec_file)
        frame_nav.pack(fill=tk.X, pady=4)
        
        app.btn_first = ttk.Button(frame_nav, text="⏮", width=4, state=tk.DISABLED, command=app.foto_prima)
        app.btn_first.pack(side=tk.LEFT, padx=(0, 2))
        
        app.btn_prev = ttk.Button(frame_nav, text="◀ Prec.", state=tk.DISABLED, command=app.foto_precedente)
        app.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        app.btn_next = ttk.Button(frame_nav, text="Succ. ▶", state=tk.DISABLED, command=app.foto_successiva)
        app.btn_next.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        app.btn_last = ttk.Button(frame_nav, text="⏭", width=4, state=tk.DISABLED, command=app.foto_ultima)
        app.btn_last.pack(side=tk.LEFT, padx=(2, 0))
        
        # Tendina per saltare direttamente a una foto specifica
        ttk.Label(sec_file, text="🎯 Vai alla foto:").pack(anchor=tk.W, pady=(4, 0))
        app.cmb_scelta_foto = ttk.Combobox(sec_file, state="readonly")
        app.cmb_scelta_foto.pack(fill=tk.X, pady=(0, 4))
        
        # NUOVO: Pulsante "Applica Impostazioni Precedente" sotto la tendina
        app.btn_copia_prec = ttk.Button(sec_file, text="📋 Applica Impostazioni Precedente", 
                                        state=tk.DISABLED, command=app.applica_impostazioni_foto_precedente)
        app.btn_copia_prec.pack(fill=tk.X, pady=(4, 2))
        ComponentiGui.crea_tooltip(app.btn_copia_prec, "Applica i parametri salvati dalla foto precedente.")
        
        # Helper interno slider
        def aggiungi_slider(contenitore, label, min_v, max_v, def_v, fmt="{:.1f}"):
            ttk.Label(contenitore, text=label).pack(anchor=tk.W, pady=(4, 0))
            frame_slider = ttk.Frame(contenitore)
            frame_slider.pack(fill=tk.X, pady=(0, 4))

            sld = ttk.Scale(frame_slider, from_=min_v, to=max_v, value=def_v)
            sld.pack(side=tk.LEFT, fill=tk.X, expand=True)

            valore_var = tk.StringVar(value=fmt.format(def_v))
            ttk.Label(frame_slider, textvariable=valore_var, width=8, anchor=tk.E).pack(side=tk.LEFT, padx=(8, 0))

            def on_slider_change(v):
                valore_var.set(fmt.format(float(v)))
                ComponentiGui.pianifica_aggiornamento_ottimizzato(app)

            sld.configure(command=on_slider_change)
            return sld

        # --- SEZIONE 2: SVILUPPO E COLORE ---
        sec_colore = ttk.LabelFrame(app.pan_sinistro, text=" 🎨 Sviluppo e Colore ", padding="8")
        sec_colore.pack(fill=tk.X, pady=5)

        app.sld_brightness = aggiungi_slider(sec_colore, "Luminosità", 0.5, 2.0, 1.0)
        app.sld_contrast = aggiungi_slider(sec_colore, "Contrasto", 0.5, 2.0, 1.0)
        app.sld_saturation = aggiungi_slider(sec_colore, "Saturazione", 0.0, 2.0, 1.0)
        app.sld_sharpness = aggiungi_slider(sec_colore, "Nitidezza (Sharpness)", 100, 300, 100)
        app.sld_denoise = aggiungi_slider(sec_colore, "Riduzione Disturbo (Denoise)", 0.0, 5.0, 0.0)

        app.var_bw = tk.BooleanVar(value=False)
        ttk.Checkbutton(sec_colore, text="Converti in Bianco e Nero", variable=app.var_bw, 
                        command=app.gestisci_modalita_colore).pack(fill=tk.X, pady=4)

        # --- SEZIONE 3: GEOMETRIA E CORREZIONE ---
        sec_geom = ttk.LabelFrame(app.pan_sinistro, text=" 📐 Geometria e Ritaglio ", padding="8")
        sec_geom.pack(fill=tk.X, pady=5)
        
        app.sld_rotation = aggiungi_slider(sec_geom, "Rotazione Angolo (°)", -45.0, 45.0, 0.0)
        app.sld_distortion = aggiungi_slider(sec_geom, "Distorsione Lente", -5.0, 5.0, 0.0)
        app.sld_crop = aggiungi_slider(sec_geom, "Ritaglio Orizzontale (Crop %)", 0.0, 40.0, 0.0)
        app.sld_margine = aggiungi_slider(sec_geom, "Ritaglio Verticale (Margine %)", 0.0, 40.0, 0.0)

        # --- SEZIONE 4: AZIONI E FINALIZZAZIONE ---
        sec_azione = ttk.LabelFrame(app.pan_sinistro, text=" ⚙️ Azioni di Output ", padding="8")
        sec_azione.pack(fill=tk.X, pady=5)

        app.btn_macchie = ttk.Button(sec_azione, text="🧹 Attiva Pennello Macchie", command=app.attiva_strumento_macchie)
        app.btn_macchie.pack(fill=tk.X, pady=3)
        ComponentiGui.crea_tooltip(app.btn_macchie, "Attiva/disattiva lo strumento penna per ritocco macchie.")

        app.btn_lightbox = ttk.Button(sec_azione, text="🖼️ Anteprima Lightbox", command=app.apri_lightbox)
        app.btn_lightbox.pack(fill=tk.X, pady=3)
        ComponentiGui.crea_tooltip(app.btn_lightbox, "Apri un overlay di anteprima a schermo intero dell'immagine corrente.")

        ttk.Button(sec_azione, text="🔄 Reset Vista / Annulla Zoom", command=app.interazione.annulla_zoom).pack(fill=tk.X, pady=3)

        app.var_esportare = tk.BooleanVar(value=True)
        chk_batch = ttk.Checkbutton(sec_azione, text="Seleziona Foto per Batch", variable=app.var_esportare,
                        command=app.gestisci_interazione_spunta)
        chk_batch.pack(fill=tk.X, pady=4)
        ComponentiGui.crea_tooltip(chk_batch, "Marca o demarca la foto corrente per le operazioni batch.")

        btn_salva = ttk.Button(sec_azione, text="💾 Salva Foto Corrente...", command=app.apri_dialog_esportazione_singola)
        btn_salva.pack(fill=tk.X, pady=3)
        ComponentiGui.crea_tooltip(btn_salva, "Salva l'immagine corrente con i parametri selezionati.")

        btn_batch = ttk.Button(sec_azione, text="🚀 AVVIA BATCH SULLE SELEZIONATE", command=app.esegui_batch_completo)
        btn_batch.pack(fill=tk.X, pady=3)
        ComponentiGui.crea_tooltip(btn_batch, "Esegui l'elaborazione batch sulle foto selezionate.")

        sec_help = ttk.LabelFrame(app.pan_sinistro, text=" 🛈 Guida Rapida ", padding="8")
        sec_help.pack(fill=tk.X, pady=5)
        ttk.Label(sec_help, text="Doppio click: zoom | Esc: torna normale | Pennello macchie: correggi difetti | Usa i slider per regolare la resa visiva.",
                  wraplength=300, justify=tk.LEFT).pack(fill=tk.X)
