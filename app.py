import os
import gradio as gr
from google import genai
from google.genai import types

# ── API ───────────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
Eres un asistente de retroalimentación pedagógica para docentes universitarios en México que
están diseñando microaprendizajes (unidades de 3-7 minutos). Tu función es evaluar y retroalimentar
su OBJETIVO, GANCHO, CONTENIDO y ACCIÓN.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RÚBRICA DE EVALUACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OBJETIVO:
• Nivel 3 (Sólido): verbo observable, una sola idea, contexto específico, verificable en 2 minutos
• Nivel 2 (En desarrollo): verbo observable pero contenido amplio, o contexto vago, o dos ideas con "y"
• Nivel 1 (Requiere revisión): verbo no observable, es tema en lugar de objetivo, o imposible verificar
GANCHO:
• Nivel 3 (Sólido): genera pregunta activa, conecta experiencia previa, no revela respuesta
• Nivel 2 (En desarrollo): llama atención pero no activa previo, o pregunta sin tensión real
• Nivel 1 (Requiere revisión): es título, lista de objetivos, intro expositiva, o solo anuncia tema
CONTENIDO:
• Nivel 3 (Sólido): una idea central, todo justificado por objetivo, sin ruido, formato adecuado
• Nivel 2 (En desarrollo): idea clara pero con elementos decorativos que no contribuyen
• Nivel 1 (Requiere revisión): múltiples ideas sin jerarquía, o enciclopédico, o formato contradice objetivo
ACCIÓN:
• Nivel 3 (Sólido): aplica lo aprendido, tarea verificable, retroalimentación inmediata y diferenciada
• Nivel 2 (En desarrollo): hace algo pero memorístico o no requiere aplicar contenido específico
• Nivel 1 (Requiere revisión): no hay acción, o decorativa sin criterio, o solo "correcto/incorrecto"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EJEMPLOS BUENOS Y MALOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OBJETIVOS BUENOS:
"Al terminar, el estudiante podrá identificar si un acuerdo informal cumple los tres elementos
esenciales de un contrato válido usando un caso cotidiano."
"Al terminar, el estudiante podrá clasificar cinco alimentos de un menú escolar según el plato
del bien comer."
OBJETIVOS MALOS:
"Que el estudiante comprenda la importancia de la alimentación saludable." → verbo no observable
"Que el estudiante conozca el proceso administrativo y aplique sus fases en su empresa." → dos verbos
GANCHOS BUENOS:
"Un estudio de Stanford encontró que el 82% de los universitarios no distingue una noticia real
de una patrocinada. ¿Tus estudiantes estarían en ese porcentaje?"
"Piensa en la última compra importante que hiciste en línea. ¿Buscaste las mejores opciones
o buscaste confirmación de lo que ya querías comprar?"
GANCHOS MALOS:
"En esta lección aprenderás los tres criterios para evaluar fuentes." → anuncia, no provoca
"Bienvenido a este módulo sobre sesgo de confirmación." → intro expositiva
CONTENIDOS BUENOS:
Tres diapositivas, una por criterio: autoría, respaldo, contexto. Cada una con título, pregunta
clave, regla aplicable. Sin intro, sin resumen.
CONTENIDOS MALOS:
12 diapositivas sobre "todo sobre contratos": historia, tipos, cláusulas, jurisprudencia.
Video que empieza con contexto histórico innecesario.
ACCIONES BUENOS:
"Un artículo sin referencias afirma que el 70% de jóvenes prefieren videos. Usando tres criterios,
¿cómo lo clasificarías?" (4 opciones, respuesta correcta con explicación diferenciada)
"Arrastra estas afirmaciones a columna correcta: ¿apoya libre albedrío o determinismo?"
ACCIONES MALAS:
"¿Qué aprendiste? Escríbelo en dos líneas." → no verifica objetivo
"Verdadero o Falso: El microaprendizaje es una estrategia." → memorístico
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TU TONO Y VOZ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Académico con calor. Eres colega que conoce diseño instruccional, no evaluador.
- Usa "tú" directo. Sin usted.
- Nombra exactamente qué funciona y qué no, en términos pedagógicos concretos.
- Una o dos preguntas al final para provocar reflexión, no para llenar formulario.
- NUNCA uses: "¡Excelente!", "¡Muy bien!", "¡Fantástico!", "innovador", "dinámico", "transformador"
- Si algo está bien, lo dices con precisión. Si necesita ajuste, lo dices igual.
- Acompaña sin sustituir el juicio del docente.
- Respuestas CONCISAS: máximo 4-5 líneas por elemento evaluado.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TU FLUJO CONVERSACIONAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASO 1 — Solo cuando inicia la conversación:
Saluda cálidamente en máximo 3 líneas. Explica brevemente tu rol.
Pide que copie y pegue su OBJETIVO.
PASO 2 — Cuando el docente comparte su objetivo:
Retroalimenta el objetivo en máximo 4-5 líneas (nivel alcanzado, qué funciona, qué ajustar).
Luego pide que describa GANCHO, CONTENIDO y ACCIÓN (puede ser en uno o tres mensajes).
PASO 3 — Cuando el docente comparte gancho, contenido y acción:
Retroalimenta cada elemento en máximo 4-5 líneas cada uno.
Incluye el nivel de la rúbrica alcanzado para cada uno.
Al final: "¿Tienes dudas sobre algo específico? Podemos explorar más."
PASO 4 — Rondas adicionales sin límite:
Responde preguntas, aclara, profundiza en lo que pida el docente.
PASO 5 — Cierre (cuando el docente diga que terminó):
"Bien. Ahora puedes cerrar esta pestaña y continuar con tu microaprendizaje.
Confío en que el recurso que producirás funcionará con tus estudiantes."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESTRICCIONES DURAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Trabaja SOLO con lo que el docente compartió. No inventes información.
- NO evalúes calidad técnica de herramientas (Wayground, NotebookLM, etc.)
- NO opines sobre el tema disciplinar del docente
- NO pidas rehacer todo desde cero; una cosa a la vez
- NO apruebes diseños malos por amabilidad
- NO evalúes redacción ni estilo del docente
- Si pregunta sobre temas disciplinares, responde brevemente y retorna al diseño instruccional
- NUNCA uses adulación vacía
"""

WELCOME_MSG = (
    "Hola. Estoy aquí para acompañarte en el diseño de tu microaprendizaje. "
    "Mi función es darte retroalimentación específica sobre tu objetivo, gancho, "
    "contenido y acción, usando criterios de diseño instruccional.\n\n"
    "Para empezar: copia y pega tu **OBJETIVO** tal como lo tienes redactado."
)

# ── Lógica de respuesta ───────────────────────────────────────────────────────
def _extract_text(msg) -> str:
    if isinstance(msg, str):
        return msg
    elif isinstance(msg, list):
        texts = []
        for part in msg:
            if isinstance(part, dict) and "text" in part:
                texts.append(part["text"])
            elif isinstance(part, str):
                texts.append(part)
        return " ".join(texts) if texts else str(msg)
    elif isinstance(msg, dict):
        if "text" in msg:
            return msg["text"]
    return str(msg)

def respond(message, history: list) -> str:
    """
    Recibe el mensaje del usuario y el historial en formato
    [{"role": "user"|"assistant", "content": str}, ...]
    y devuelve la respuesta como string.
    """
    if not client:
        gr.Warning("⚠️ No se encontró la clave de API. Configura GOOGLE_API_KEY en los Secrets del Space.")
        return "⚠️ No se encontró la clave de API. Configura GOOGLE_API_KEY en los Secrets del Space."
    try:
        contents = []
        for item in history:
            role    = item.get("role", "")
            content = _extract_text(item.get("content", ""))
            if role == "user":
                contents.append(
                    types.Content(role="user",  parts=[types.Part(text=content)])
                )
            elif role == "assistant":
                contents.append(
                    types.Content(role="model", parts=[types.Part(text=content)])
                )

        contents.append(
            types.Content(role="user", parts=[types.Part(text=_extract_text(message))])
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1024,
                temperature=0.7,
            ),
        )
        return response.text

    except Exception as e:
        err = str(e).lower()
        if any(k in err for k in ("429", "quota", "resource_exhausted")):
            return "⚠️ Límite de consultas alcanzado hoy. Intenta mañana o en unos minutos."
        return f"⚠️ Error al conectar con Gemini: {e}"


# ── Tema Gradio ───────────────────────────────────────────────────────────────
custom_theme = gr.themes.Soft(
    font=[gr.themes.GoogleFont("Montserrat"), "Helvetica", "Arial", "sans-serif"],
    primary_hue="red",
    neutral_hue="slate",
    radius_size=gr.themes.sizes.radius_lg,
    text_size=gr.themes.sizes.text_md,
).set(
    body_background_fill="#ffffff",
    body_text_color="#1a1a1a",
    body_text_color_subdued="#4a4a4a",
    background_fill_primary="#ffffff",
    background_fill_secondary="#fafafa",
    border_color_primary="rgba(0,0,0,0.02)",
    block_background_fill="#ffffff",
    block_border_width="1px",
    block_border_color="rgba(0,0,0,0.02)",
    block_radius="32px",
    block_shadow="0 20px 60px rgba(0,0,0,0.05)",
    container_radius="32px",
    input_background_fill="#fafafa",
    input_border_color="#e5e5e5",
    input_border_width="1px",
    input_radius="16px",
    button_primary_background_fill="#AB1E12",
    button_primary_background_fill_hover="#89180e",
    button_primary_text_color="#ffffff",
    button_primary_border_color="#AB1E12",
    button_large_radius="50px",
    button_small_radius="50px",
    panel_background_fill="#ffffff",
    color_accent="#AB1E12",
)

# ── Componentes ───────────────────────────────────────────────────────────────
custom_chatbot = gr.Chatbot(
    value=[{"role": "assistant", "content": WELCOME_MSG}],
    height=500,
    show_label=False,
    avatar_images=(None, None),
)

# submit_btn se pasa directamente al Textbox en Gradio 6
custom_textbox = gr.Textbox(
    placeholder="Escribe aquí tu respuesta y presiona Enter o el botón Enviar →",
    show_label=False,
    lines=2,
    max_lines=6,
    container=True,
    interactive=True,
    submit_btn="Enviar ↩",
)

# ── Interfaz ──────────────────────────────────────────────────────────────────
with gr.Blocks(title="Asistente de Retroalimentación Pedagógica") as demo:

    gr.HTML("""
    <div style="text-align: center; max-width: 900px; margin: 40px auto 32px auto; font-family: 'Montserrat', Helvetica, Arial, sans-serif;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 16px;">
            <span style="display: inline-block; padding: 6px 16px; background-color: rgba(171,30,18,0.08); color: #AB1E12; font-weight: 700; font-size: 15px; letter-spacing: 0.1em; border-radius: 50px;">ASISTENTE IA</span>
            <h1 style="margin: 0; font-size: 32px; font-weight: 800; color: #1a1a1a; line-height: 1.2; letter-spacing: -0.02em;">Retroalimentación Pedagógica</h1>
        </div>
        <p style="margin: 0 auto; font-size: 16px; font-weight: 400; color: #4a4a4a; line-height: 1.8; max-width: 680px;">Diseño instruccional — Objetivo · Gancho · Contenido · Acción</p>
    </div>
    """)

    gr.ChatInterface(
        fn=respond,
        chatbot=custom_chatbot,
        textbox=custom_textbox,
        stop_btn=False,
        title=None,
    )

    gr.HTML("""
    <div style="text-align: center; margin-top: 32px; margin-bottom: 40px; font-family: 'Montserrat', Helvetica, Arial, sans-serif;">
        <p style="margin: 0; font-size: 13px; font-weight: 500; color: #888888;">La conversación no se guarda · Cada sesión es independiente</p>
    </div>
    """)

# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        ssr_mode=False,
        theme=custom_theme,
    )
