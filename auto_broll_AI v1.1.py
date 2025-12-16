import os
import re
import json
import time
import random
import tempfile
import requests
import unidecode
import subprocess
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import whisper

# ============================================
# LOGGING
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_broll_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIG
# ============================================
AUDIO_FILE = "Audio3.mp3"
VIDEO_FOLDER = "clips"

FPS = 24
MIN_CLIP_DURATION = 5
MAX_CLIPS_PER_SEGMENT = 3

PIXABAY_API_KEY = "53273901-713481804e4258f779d3a115a"
PEXELS_API_KEY = "Vtne58Q3C5hAZS44F3byFA0AiLWBDiS2lySLsrdBwKSlGYV3YPOws4F0"

os.makedirs(VIDEO_FOLDER, exist_ok=True)

# ============================================
# UTILIDADES
# ============================================
def safe_filename(text, max_length=50):
    text = unidecode.unidecode(text)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '_', text)
    return text[:max_length]

# ============================================
# TRANSCRIPCIÓN
# ============================================
def transcribe_audio(audio_file):
    logger.info("Iniciando transcripción de audio...")
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_file, word_timestamps=True, language="es")
        segments = []
        for s in result.get("segments", []):
            segments.append({
                "text": s["text"].strip(),
                "start": s["start"],
                "end": s["end"],
                "duration": s["end"] - s["start"]
            })
        logger.info(f"Transcripción completada: {len(segments)} segmentos encontrados")
        return segments
    except Exception as e:
        logger.error(f"Error en transcripción: {e}", exc_info=True)
        return []

# ============================================
# DESCARGA DE CLIPS
# ============================================
def descargar_clip(url: str, query: str, idx: int) -> Optional[str]:
    filename = os.path.join(VIDEO_FOLDER, f"{safe_filename(query)}_{int(time.time())}_{idx}.mp4")

    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)

        # Validar clip descargado
        clip = VideoFileClip(filename)
        if clip.duration < 1:
            clip.close()
            os.remove(filename)
            return None
        clip.close()

        return filename

    except Exception as e:
        logger.warning(f"Error descargando clip {url}: {e}")
        if os.path.exists(filename):
            os.remove(filename)
        return None


def buscar_pixabay(query):
    url = "https://pixabay.com/api/videos/"
    params = {"key": PIXABAY_API_KEY, "q": query, "per_page": MAX_CLIPS_PER_SEGMENT}

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        hits = r.json().get("hits", [])
        results = []
        for i, hit in enumerate(hits[:MAX_CLIPS_PER_SEGMENT]):
            video = hit.get("videos", {}).get("large")
            if video and video.get("url"):
                path = descargar_clip(video["url"], query, i)
                if path:
                    results.append(path)
        return results

    except:
        return []


def buscar_pexels(query):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": MAX_CLIPS_PER_SEGMENT}

    try:
        r = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=15)
        r.raise_for_status()
        videos = r.json().get("videos", [])
        results = []
        for i, v in enumerate(videos[:MAX_CLIPS_PER_SEGMENT]):
            files = v.get("video_files", [])
            if not files:
                continue
            best = max(files, key=lambda x: x.get("width", 0))
            if best.get("link"):
                path = descargar_clip(best["link"], query, i)
                if path:
                    results.append(path)
        return results

    except:
        return []

# ============================================
# NORMALIZAR CLIP (FFMPEG)
# ============================================
def normalizar_clip(path):
    if not os.path.exists(path):
        return None

    out = path.replace(".mp4", "_norm.mp4")

    if os.path.exists(out):
        try:
            clip = VideoFileClip(out)
            if clip.duration > 1:
                clip.close()
                return out
            clip.close()
        except:
            os.remove(out)

    cmd = [
        "ffmpeg", "-y", "-i", path,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", out
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return out
    except:
        if os.path.exists(out):
            os.remove(out)
        return None

# ============================================
# CARGA SEGURA DEL CLIP (SIN WITH)
# ============================================
def cargar_clip_seguro(path):
    try:
        clip = VideoFileClip(path)
        if clip.duration is None or clip.duration <= 0:
            clip.close()
            return None
        return clip
    except:
        return None

# ============================================
# CREACIÓN DEL VIDEO FINAL (VERSIÓN ESTABLE)
# ============================================
def crear_video(segmentos_ia, original_segments):

    audio = AudioFileClip(AUDIO_FILE)
    audio_dur = audio.duration

    final_clips = []

    used = set()

    # Generar lista de rutas válidas
    for seg, orig in zip(segmentos_ia, original_segments):
        ideas = seg.get("clips", [])

        elegido = None
        for idea in ideas:
            paths = buscar_pixabay(idea) or buscar_pexels(idea)
            paths = [p for p in paths if p not in used]
            if paths:
                elegido = normalizar_clip(paths[0])
                if elegido:
                    used.add(elegido)
                    final_clips.append((elegido, orig["duration"]))
                    break

    if not final_clips:
        logger.error("No hay clips finales para montar el video.")
        return

    # Construcción segura de VideoClips
    video_clips = []

    for path, dur in final_clips:
        clip = cargar_clip_seguro(path)
        if clip is None:
            continue

        dur = min(max(dur, MIN_CLIP_DURATION), 25)

        if clip.duration > dur:
            start = random.uniform(0, clip.duration - dur)
            sub = clip.subclip(start, start + dur)
        else:
            reps = int(dur // clip.duration) + 1
            sub = concatenate_videoclips([clip] * reps).subclip(0, dur)

        video_clips.append(sub)

    if not video_clips:
        logger.error("Todos los clips fallaron.")
        return

    final = concatenate_videoclips(video_clips, method="compose")

    if final.duration > audio_dur:
        final = final.subclip(0, audio_dur)

    final = final.set_audio(audio)

    out = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    logger.info(f"Renderizando video final en {out}...")

    final.write_videofile(
        out,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        threads=4,
        temp_audiofile="temp_audio.m4a",
        remove_temp=True
    )

    logger.info(f"VIDEO GUARDADO: {out}")

    # Limpieza manual
    final.close()
    audio.close()


# ============================================
# MAIN
# ============================================
def main():
    logger.info("=== INICIANDO ===")

    segments = transcribe_audio(AUDIO_FILE)

    if not segments:
        logger.error("No se pudo transcribir el audio.")
        return

    segmentos_ia = [
        {"texto": s["text"], "clips": ["nature", "city", "tech"]}
        for s in segments
    ]

    crear_video(segmentos_ia, segments)

    logger.info("=== FINALIZADO ===")


if __name__ == "__main__":
    main()
