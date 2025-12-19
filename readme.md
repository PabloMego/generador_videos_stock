# 🎬 Generador Automático de Vídeos a partir de Audio (IA)

Este proyecto convierte **audio en vídeo completamente editado de forma automática**.  
Le das un audio, el programa lo transcribe, busca vídeos de stock relacionados, los monta, sincroniza todo y te entrega un **MP4 listo para publicar**.

Tú no editas.  
Tú no buscas clips.  
Tú no haces nada.  
Magia pura 🎬✨

---

## 🧠 ¿Qué hace exactamente? (versión sin tecnicismos)

Tienes un audio (podcast, locución, narración, lo que sea), se lo pasas al programa y:

1️⃣ Transcribe el audio automáticamente usando IA  
2️⃣ Divide el contenido en segmentos por tema  
3️⃣ Busca clips relacionados en **Pixabay** y **Pexels**  
4️⃣ Descarga y normaliza todos los vídeos a **1920x1080**  
5️⃣ Sincroniza cada clip con su parte del audio  
6️⃣ Genera un vídeo final completamente montado  

Resultado: un vídeo listo para YouTube sin abrir ningún editor.

---

## ✨ Lo que lo hace especial

🤖 **Transcripción automática con IA**  
Usa **OpenAI Whisper** para convertir el audio a texto.  
Detecta automáticamente el idioma y genera timestamps precisos sin configuración previa 🧠

---

🔍 **Búsqueda inteligente de clips**  
Analiza cada segmento del audio y busca vídeos relacionados en Pixabay y Pexels.  
Si no encuentra resultados, prueba con sinónimos automáticamente.  
Es como tener un editor que sabe exactamente qué buscar.

---

📹 **Descarga y normalización automática**  
Todos los clips se:
- Redimensionan a **1920x1080 (Full HD)**
- Comprimen con **FFmpeg**
- Ajustan para que tengan calidad consistente  

Todo sin intervención manual 🪄

---

⏱️ **Sincronización perfecta audio–vídeo**  
Cada clip dura exactamente lo que dura su segmento de audio:
- Si el clip es corto → se repite
- Si es largo → se recorta  

Resultado: sincronización pixel-perfect ⏰

---

🎬 **Montaje automático completo**  
Concatena todos los clips, añade el audio original y genera un **MP4 listo para subir**.  
Sin CapCut. Sin Premiere. Sin tocar nada 🚀

---

📋 **Logging detallado**  
Guarda un log con cada paso del proceso.  
Si algo falla, sabes exactamente qué pasó y dónde. Debugging sin estrés 😎

---

## 🎭 Cómo funciona (la magia detrás del telón)

Es un script **100% backend en Python**, sin interfaz gráfica.  
Ejecutas el script, le pasas un audio y el sistema se encarga del resto.

### Flujo de trabajo

1️⃣ **Transcribir audio**  
Carga el archivo de audio y Whisper genera la transcripción con timestamps exactos.

2️⃣ **Buscar clips de stock**  
Por cada segmento, busca vídeos relacionados en Pixabay y Pexels.  
Descarga varios clips por segmento para tener opciones.

3️⃣ **Normalizar clips**  
Usa FFmpeg para convertir todos los vídeos a Full HD y comprimirlos de forma uniforme.

4️⃣ **Ajustar duración**  
Cada clip se adapta exactamente a la duración de su segmento de audio.

5️⃣ **Montar vídeo final**  
Concatena todos los clips, añade el audio original y renderiza el vídeo final a 24 FPS usando múltiples threads 🚀

---

## 🛠️ Stack técnico

- 🐍 **Python** – base del proyecto  
- 🤖 **OpenAI Whisper** – transcripción automática con timestamps  
- 🎬 **MoviePy** – montaje, sincronización y render final  
- 🎥 **FFmpeg** – normalización, redimensionado y compresión  
- 🌐 **Pixabay API** – búsqueda de clips de stock  
- 🌐 **Pexels API** – clips adicionales de stock  
- 📊 **Requests + JSON** – comunicación con APIs y manejo de datos  
- ⚙️ **Threading** – descargas en paralelo para mayor velocidad  

---

## 👥 ¿Para quién es este proyecto?

✅ **Podcasters**  
Convierte episodios de audio en vídeos para YouTube automáticamente 🎙️➡️🎬

✅ **Creadores de contenido educativo**  
Audios de clases o tutoriales transformados en vídeos visuales sin editar 🎓

✅ **Productores de vídeo perezosos (pero listos)**  
No más horas buscando clips de stock. Que el script lo haga por ti ☕

✅ **Agencias de contenido**  
Genera grandes volúmenes de vídeos en poco tiempo y reduce costes ⚡

✅ **YouTubers de alto volumen**  
Deja el script trabajando mientras duermes y despierta con vídeos listos 😴➡️💰

---

## 🚀 Uso básico

```bash
pip install -r requirements.txt
python main.py audio.mp3
