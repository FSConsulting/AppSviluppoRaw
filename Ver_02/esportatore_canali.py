"""Esportazione e ricampionamento per canali target (stampa/social/web).

Questo modulo contiene helper per generare versioni derivate delle
immagini (stampa, social, web) con ricampionamento e salvataggio in
cartelle separate. Le funzioni sono progettate per essere usate in
processi batch o singole esportazioni tramite la UI.
"""

import os
from PIL import Image
from motore_sviluppo import MotoreSviluppo

class EsportatoreCanali:
    """Gestisce il ricampionamento mirato e l'esportazione batch automatica in cartelle dedicate.

    Esempio
    -------
    Per esportare un batch, la UI raccoglie una coda di tuple ``(nome_file, params)``
    e chiama::

        EsportatoreCanali.esegui_esportazione_batch(cartella_base, coda, callback_progresso)

    """

    @staticmethod
    def _ridimensiona_lato_corto(img: Image.Image, target_corto: int) -> Image.Image:
        w, h = img.size
        if w <= h:
            nuova_w = target_corto
            nuova_h = int(h * (target_corto / w))
        else:
            nuova_h = target_corto
            nuova_w = int(w * (target_corto / h))
        return img.resize((nuova_w, nuova_h), Image.Resampling.LANCZOS)

    @staticmethod
    def elabora_e_salva(canale: str, percorso_raw: str, params: dict, dest_path: str):
        img = MotoreSviluppo.estrai_immagine_nativa(percorso_raw, forza_colore=not params['is_bw'])
        img = MotoreSviluppo.applica_editing(
            img, params['brightness'], params['contrast'], params['saturation'],
            params['sharpness'], params['denoise'], params['rotation'],
            params['distortion'], params['crop'], params['margine'], params['is_bw']
        )

        if canale == "stampa":
            target_corto_px = int((20 / 2.54) * 300)
            img = EsportatoreCanali._ridimensiona_lato_corto(img, target_corto_px)
            img.save(dest_path, "JPEG", quality=100, dpi=(300, 300))
        elif canale == "social":
            img = EsportatoreCanali._ridimensiona_lato_corto(img, 1080)
            img.save(dest_path, "JPEG", quality=100)
        elif canale == "web":
            img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
            img.save(dest_path, "JPEG", quality=98)

    @staticmethod
    def esegui_esportazione_batch(cartella_base: str, coda: list, callback_progresso=None):
        """Genera le tre cartelle di output ed esporta i tre formati, notificando l'avanzamento."""
        dir_stampa = os.path.join(cartella_base, "AutoStampa")
        dir_social = os.path.join(cartella_base, "AutoSocial")
        dir_web = os.path.join(cartella_base, "AutoWeb")

        for d in [dir_stampa, dir_social, dir_web]:
            os.makedirs(d, exist_ok=True)

        for i, (nome_file, params) in enumerate(coda):
            percorso_raw = os.path.join(cartella_base, nome_file)
            nome_puro = os.path.splitext(nome_file)[0]
            
            if not os.path.exists(percorso_raw):
                continue

            # Se presente una callback, aggiorna lo stato visivo prima di iniziare l'elaborazione pesante
            if callback_progresso:
                callback_progresso(i + 1, len(coda), nome_file)

            EsportatoreCanali.elabora_e_salva("stampa", percorso_raw, params, os.path.join(dir_stampa, f"{nome_puro}.jpg"))
            EsportatoreCanali.elabora_e_salva("social", percorso_raw, params, os.path.join(dir_social, f"{nome_puro}.jpg"))
            EsportatoreCanali.elabora_e_salva("web", percorso_raw, params, os.path.join(dir_web, f"{nome_puro}.jpg"))
