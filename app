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
def respond(message: str, history: list) -> str:
    """
    Recibe el mensaje del usuario y el historial en formato
    [{"role": "user"|"assistant", "content": str}, ...]
    y devuelve la respuesta como string.
    """
    if not client:
        return (
            "⚠️ No se encontró la clave de API. "
            "Configura GOOGLE_API_KEY en los Secrets del Space."
        )
    try:
        contents = []
        for item in history:
            role    = item.get("role", "")
            content = item.get("content", "")
            if role == "user":
                contents.append(
                    types.Content(role="user",  parts=[types.Part(text=content)])
                )
            elif role == "assistant":
                contents.append(
                    types.Content(role="model", parts=[types.Part(text=content)])
                )

        contents.append(
            types.Content(role="user", parts=[types.Part(text=message)])
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
        if any(k in err for k in ("quota", "rate", "limit", "429")):
            return "⚠️ Límite de consultas alcanzado hoy. Intenta mañana o en unos minutos."
        return f"⚠️ Error al conectar con Gemini: {e}"


# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
:root {
    --bg:         #0f1117;
    --surface:    #1a1d27;
    --accent:     #6c7bff;
    --accent-dim: #2d3578;
    --text:       #e8eaf6;
    --muted:      #8b91c7;
    --border:     #2e3250;
    --user-bg:    #1e2340;
    --r:          12px;
}
*, *::before, *::after { box-sizing: border-box; }
body,
.gradio-container,
.gradio-container > .main,
footer {
    background: var(--bg) !important;
}
* { font-family: 'DM Sans', system-ui, sans-serif !important; }
/* ── Header ── */
.app-header {
    text-align: center;
    padding: 1.8rem 1rem 0.8rem;
}
.app-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.02em;
    margin: 0 0 0.25rem;
}
.app-header p {
    color: var(--muted);
    font-size: 0.86rem;
    margin: 0;
}
.accent { color: var(--accent); }
/* ── Chatbot ── */
.chatbot-wrap,
.chatbot-wrap > div {
    background: var(--surface) !important;
}
.chatbot-wrap {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
}
/* Burbujas usuario */
.message.user > div {
    background: var(--user-bg) !important;
    border: 1px solid var(--accent-dim) !important;
    border-radius: 10px 10px 2px 10px !important;
    color: var(--text) !important;
    padding: 0.65rem 0.9rem !important;
}
/* Burbujas bot */
.message.bot > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px 10px 10px 2px !important;
    color: var(--text) !important;
    padding: 0.65rem 0.9rem !important;
}
/* Ocultar avatares */
.avatar-container,
.message-avatar { display: none !important; }
/* ── Textbox (input) ── */
.input-wrap textarea,
textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    color: var(--text) !important;
    font-size: 0.94rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.15s;
}
textarea:focus {
    border-color: var(--accent) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(108,123,255,0.14) !important;
}
textarea::placeholder { color: var(--muted) !important; }
/* ── Botón Enviar ── */
button.primary,
button[class*="primary"] {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-weight: 600 !important;
    transition: opacity 0.15s !important;
}
button.primary:hover { opacity: 0.82 !important; }
/* ── Footer ── */
.app-footer {
    text-align: center;
    padding: 0.5rem;
    color: var(--muted);
    font-size: 0.76rem;
}
/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
"""

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
with gr.Blocks(title="Asistente de Retroalimentación Pedagógica") as demo:

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
