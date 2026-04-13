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
            model="gemini-1.5-flash",
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


# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = ""
# ── Componentes ───────────────────────────────────────────────────────────────
custom_chatbot = gr.Chatbot(
    value=[{"role": "assistant", "content": WELCOME_MSG}],
    elem_classes=["chatbot-wrap"],
    height=500,
    show_label=False,
)

# submit_btn se pasa directamente al Textbox en Gradio 6
custom_textbox = gr.Textbox(
    placeholder="Escribe aquí y presiona Enter o el botón Enviar →",
    show_label=False,
    lines=2,
    max_lines=6,
    container=True,
    interactive=True,
    submit_btn="Enviar ↩",
)

# ── Interfaz ──────────────────────────────────────────────────────────────────
# gr.ChatInterface gestiona el input/output de forma nativa:
# el campo de texto SIEMPRE es visible y funcional.
with gr.Blocks(title="Asistente de Retroalimentación Pedagógica", theme=gr.themes.Soft(primary_hue="indigo", neutral_hue="slate")) as demo:

    gr.HTML("""
    <div class="app-header">
        <h1>Retroalimentación Pedagógica <span class="accent">·</span> Microaprendizaje</h1>
        <p>Diseño instruccional — Objetivo · Gancho · Contenido · Acción</p>
    </div>
    """)

    gr.ChatInterface(
        fn=respond,
        chatbot=custom_chatbot,
        textbox=custom_textbox,
        stop_btn=False,
        title=None,
    )

    gr.HTML(
        '<div class="app-footer">'
        "La conversación no se guarda · Cada sesión es independiente"
        "</div>"
    )

# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CSS,
    )
