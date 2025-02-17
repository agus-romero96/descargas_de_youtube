# -*- coding: utf-8 -*-
try:
    import re
    from youtube_transcript_api import YouTubeTranscriptApi
    from mi_logging import logger
    logger.info("Módulos importados en extraccion_subtitulos.py")
except ImportError as e:
    logger.critical("Error al importar módulos en extraccion_subtitulos.py: %s", e)
    raise

def obtener_id_video(url):
    """Extrae el ID del video de YouTube desde la URL."""
    patron = r"(?:v=|youtu\.be/|embed/|shorts/|v/|/videos/|watch\?v=)([a-zA-Z0-9_-]{11})"
    coincidencia = re.search(patron, url)
    if coincidencia:
        video_id = coincidencia.group(1)
        logger.info("Video ID obtenido: %s", video_id)
        return video_id
    else:
        logger.error("No se pudo extraer el ID del video.")
        return None

def obtener_nombre_video(id_video):
    """Devuelve un nombre ficticio para el video (puedes implementar la API de YouTube Data en el futuro)."""
    nombre = f"video_{id_video}"
    logger.info("Nombre del video obtenido: %s", nombre)
    return nombre

def obtener_subtitulos(id_video, idioma='es'):
    """Obtiene los subtítulos del video en el idioma especificado."""
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(id_video)
        transcript = None
        # Intentar obtener el transcript manualmente
        try:
            transcript = transcripts.find_manually_created_transcript([idioma])
            logger.info("Se encontró subtítulo manual.")
        except Exception as e_manual:
            logger.warning("No se encontró subtítulo manual: %s. Se intentará con el generado automáticamente.", e_manual)
            try:
                transcript = transcripts.find_generated_transcript([idioma])
                logger.info("Se encontró subtítulo generado automáticamente.")
            except Exception as e_generated:
                logger.error("No se encontraron subtítulos en el idioma '%s': %s", idioma, e_generated)
                return f"No se encontraron subtítulos disponibles en el idioma '{idioma}'."
        subtitle_data = transcript.fetch()
        subtitulos = '\n'.join([entrada['text'] for entrada in subtitle_data])
        logger.info("Subtítulos extraídos con éxito.")
        return subtitulos
    except Exception as e:
        logger.error("Error al obtener subtítulos: %s", e)
        return f"Error al obtener subtítulos: {e}"

def guardar_subtitulos_en_archivo(subtitulos, nombre_archivo="subtitulos.txt"):
    """
    Guarda los subtítulos extraídos en un archivo de texto.
    Si no se especifica un nombre de archivo, se usará 'el id del video' en formato txt
    """
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(subtitulos)
        logger.info("Subtítulos guardados en %s", nombre_archivo)
        return f"Subtítulos guardados en {nombre_archivo}"
    except Exception as e:
        logger.error("Error al guardar el archivo: %s", e)
        return f"Error al guardar el archivo: {e}"
