"""Motore di sviluppo RAW e funzioni di manipolazione immagine.

Questo modulo espone la classe `MotoreSviluppo` che fornisce helper
statici per estrarre anteprime da file RAW, applicare catene di
editing (brightness/contrast/saturation/sharpness/denoise) e funzioni
di rimozione macchie per il ritocco locale.
"""

import os
import rawpy
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw

class MotoreSviluppo:
    """Gestore dello sviluppo dei file RAW e dei filtri grafici con Healing Brush."""

    @staticmethod
    def estrai_immagine_nativa(percorso_raw: str, forza_colore: bool = True) -> Image.Image:
        """Apre il file RAW ed estrae un'anteprima rapida scalata."""
        if not percorso_raw or not os.path.exists(percorso_raw):
            raise FileNotFoundError(f"File non trovato: {percorso_raw}")
            
        with rawpy.imread(percorso_raw) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True, 
                half_size=True, 
                no_auto_bright=True,
                output_color=rawpy.ColorSpace.sRGB
            )
            img = Image.fromarray(rgb)
            if not forza_colore:
                img = ImageOps.grayscale(img)
            return img

    @staticmethod
    def applica_editing(img_base: Image.Image, brightness: float, contrast: float, 
                        saturation: float, sharpness: float, denoise: float,
                        rotation: float, distortion: float, crop: float,
                        margine: float, macchie: list, is_bw: bool) -> Image.Image:
        """Applica la catena di filtri distruttivi e correttivi sulla foto intera."""
        if img_base is None:
            return None
            
        img = img_base.copy()

        # 1. Rimozione Macchie Sensore (Eseguita sulle coordinate native stabili)
        if macchie:
            img = MotoreSviluppo.corri_rimozione_macchie(img, macchie)

        # 2. Conversione Bianco e Nero
        if is_bw:
            img = ImageOps.grayscale(img).convert("RGB")

        # 3. Regolazioni Base (Luminosità, Contrasto, Saturazione)
        if brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness)
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)
        if saturation != 1.0 and not is_bw:
            img = ImageEnhance.Color(img).enhance(saturation)

        # 4. Riduzione Disturbo (Denoise) tramite Sfocatura Gaussiana
        if denoise > 0.0:
            img = img.filter(ImageFilter.GaussianBlur(radius=denoise * 2.0))

        # 5. Nitidezza (Sharpness)
        if sharpness > 100:
            img = ImageEnhance.Sharpness(img).enhance(sharpness / 100.0)

        # 6. Rotazione Geometrica
        if rotation != 0.0:
            img = img.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)

        # 7. Crop e Ritaglio Proporzionale Manuale
        if crop > 0.0 or margine > 0.0:
            w, h = img.size
            offset_w = int(w * (crop / 200.0))
            offset_h = int(h * (margine / 200.0))
            if (w - 2 * offset_w) > 10 and (h - 2 * offset_h) > 10:
                img = img.crop((offset_w, offset_h, w - offset_w, h - offset_h))

        return img

    @staticmethod
    def corri_rimozione_macchie(img: Image.Image, macchie: list) -> Image.Image:
        """Applica la correzione locale delle macchie usando copie area/maschera.

        Parameters
        ----------
        img : PIL.Image
            Immagine sorgente su cui operare.
        macchie : list
            Lista di tuple che descrivono le macchie. Formati accettati:
            ``(mx, my, raggio)`` o ``(dest_x, dest_y, sorg_x, sorg_y, raggio)``.

        Note
        ----
        Il metodo usa una maschera ellittica sfumata per fondere l'area
        campione (sana) con l'area da correggere.
        """
        w, h = img.size
        for riga in macchie:
            if len(riga) == 3:
                mx, my, raggio = riga
                sorg_x_def = max(0, mx - raggio * 2)
                dest_x, dest_y, sorg_x, sorg_y, raggio = mx, my, sorg_x_def, my, raggio
            elif len(riga) == 5:
                dest_x, dest_y, sorg_x, sorg_y, raggio = riga
            else:
                continue

            r_int = int(raggio)
            x0_d = max(0, int(dest_x) - r_int); y0_d = max(0, int(dest_y) - r_int)
            x1_d = min(w, int(dest_x) + r_int); y1_d = min(h, int(dest_y) + r_int)
            x0_s = max(0, int(sorg_x) - r_int); y0_s = max(0, int(sorg_y) - r_int)
            x1_s = min(w, int(sorg_x) + r_int); y1_s = min(h, int(sorg_y) + r_int)
            
            w_box = min(x1_d - x0_d, x1_s - x0_s)
            h_box = min(y1_d - y0_d, y1_s - y0_s)
            if w_box <= 4 or h_box <= 4: continue
                
            area_macchia = img.crop((x0_d, y0_d, x0_d + w_box, y0_d + h_box))
            area_sana = img.crop((x0_s, y0_s, x0_s + w_box, y0_s + h_box))
            
            maschera = Image.new("L", (w_box, h_box), 0)
            disegno = ImageDraw.Draw(maschera)
            disegno.ellipse([2, 2, w_box - 2, h_box - 2], fill=255)
            
            maschera_sfumata = maschera.filter(ImageFilter.GaussianBlur(radius=max(2.0, r_int * 0.35)))
            area_corretta = Image.composite(area_sana, area_macchia, maschera_sfumata)
            img.paste(area_corretta, (x0_d, y0_d))
            
        return img
