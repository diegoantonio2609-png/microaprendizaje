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

# ── CSS para FORZAR tema claro (incluso dentro de iframe) ─────────────────────
FORCE_LIGHT_CSS = """
/* ═══════════════════════════════════════════════════════════════
   FORZAR TEMA CLARO — sobreescribe el modo oscuro de Gradio
   cuando la app se carga en un iframe y el SO del usuario
   tiene dark mode activado.
   ═══════════════════════════════════════════════════════════════ */

/* 1. Sobreescribir las CSS variables de Gradio en modo oscuro */
.dark, :root.dark, html.dark {
    --body-background-fill: #ffffff !important;
    --body-text-color: #1a1a1a !important;
    --body-text-color-subdued: #4a4a4a !important;
    --background-fill-primary: #ffffff !important;
    --background-fill-secondary: #fafafa !important;
    --block-background-fill: #ffffff !important;
    --block-border-color: rgba(0,0,0,0.02) !important;
    --border-color-primary: rgba(0,0,0,0.02) !important;
    --input-background-fill: #fafafa !important;
    --input-border-color: #e5e5e5 !important;
    --panel-background-fill: #ffffff !important;
    --color-accent: #AB1E12 !important;
    --button-primary-background-fill: #AB1E12 !important;
    --button-primary-background-fill-hover: #89180e !important;
    --button-primary-text-color: #ffffff !important;
    --button-primary-border-color: #AB1E12 !important;
    --block-shadow: 0 20px 60px rgba(0,0,0,0.05) !important;
    --neutral-50: #fafafa !important;
    --neutral-100: #f5f5f5 !important;
    --neutral-200: #e5e5e5 !important;
    --neutral-300: #d4d4d4 !important;
    --neutral-400: #a3a3a3 !important;
    --neutral-500: #737373 !important;
    --neutral-600: #525252 !important;
    --neutral-700: #404040 !important;
    --neutral-800: #262626 !important;
    --neutral-900: #171717 !important;
    --neutral-950: #0a0a0a !important;
    --shadow-drop: rgba(0,0,0,0.05) !important;
    --shadow-drop-lg: 0 20px 60px rgba(0,0,0,0.05) !important;
    --chatbot-body-background-fill: #ffffff !important;
    --checkbox-background-color: #ffffff !important;
    --color-accent-soft: rgba(171,30,18,0.08) !important;
    --table-border-color: #e5e5e5 !important;
    --table-even-background-fill: #fafafa !important;
    --table-odd-background-fill: #ffffff !important;
    --table-row-focus: rgba(171,30,18,0.05) !important;
    color-scheme: light !important;
}

/* 2. Forzar fondos y texto en elementos principales */
.dark body,
.dark .gradio-container,
.dark .main,
.dark .wrap,
.dark .contain {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
}

/* 3. Chatbot — burbujas y fondo */
.dark .chatbot,
.dark .chatbot .messages-wrapper,
.dark .chatbot .message-wrap {
    background-color: #ffffff !important;
}

.dark .chatbot .message.bot,
.dark .chatbot .message.user {
    color: #1a1a1a !important;
}

.dark .chatbot .message.bot .message-content,
.dark .chatbot .bot .message-bubble-border {
    background-color: #fafafa !important;
    border-color: rgba(0,0,0,0.02) !important;
    color: #1a1a1a !important;
}

.dark .chatbot .message.user .message-content,
.dark .chatbot .user .message-bubble-border {
    background-color: #AB1E12 !important;
    color: #ffffff !important;
}

/* 4. Input / Textbox */
.dark textarea,
.dark input[type="text"],
.dark .textbox {
    background-color: #fafafa !important;
    color: #1a1a1a !important;
    border-color: #e5e5e5 !important;
}

/* 5. Botones */
.dark .primary,
.dark button.primary {
    background-color: #AB1E12 !important;
    color: #ffffff !important;
    border-color: #AB1E12 !important;
}

/* 6. Iconos y SVGs dentro del chatbot */
.dark .chatbot svg,
.dark .chatbot button {
    color: #4a4a4a !important;
    fill: #4a4a4a !important;
}

/* 7. Footer y otros elementos de texto */
.dark footer,
.dark .footer,
.dark p,
.dark span,
.dark h1,
.dark h2,
.dark h3 {
    color: inherit !important;
}

/* 8. Scrollbar para que no se vea oscuro */
.dark ::-webkit-scrollbar-track {
    background: #f5f5f5 !important;
}
.dark ::-webkit-scrollbar-thumb {
    background: #d4d4d4 !important;
}

/* 9. Ocultar footer nativo de Gradio ("Construido con Gradio") */
footer.svelte-1ax1toq,
footer[class*="svelte-"],
.gradio-container > footer,
.main > footer,
footer {
    display: none !important;
}
"""

# ── JS para forzar tema claro ────────────────────────────────────────────────
FORCE_LIGHT_JS = """
() => {
    // Remover clase dark inmediatamente
    document.documentElement.classList.remove('dark');
    document.documentElement.setAttribute('data-theme', 'light');
    document.documentElement.style.colorScheme = 'light';

    // Observar cambios por si Gradio la vuelve a agregar
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                if (document.documentElement.classList.contains('dark')) {
                    document.documentElement.classList.remove('dark');
                }
            }
        }
    });
    observer.observe(document.documentElement, { attributes: true });

    // Forzar meta color-scheme
    let meta = document.querySelector('meta[name="color-scheme"]');
    if (!meta) {
        meta = document.createElement('meta');
        meta.name = 'color-scheme';
        document.head.appendChild(meta);
    }
    meta.content = 'light';
}
"""

# ── Componentes ───────────────────────────────────────────────────────────────
custom_chatbot = gr.Chatbot(
    value=[{"role": "assistant", "content": WELCOME_MSG}],
    height=500,
    show_label=False,
    avatar_images=(None, None),
)

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
with gr.Blocks(
    title="Asistente de Retroalimentación Pedagógica",
    css=FORCE_LIGHT_CSS,
    js=FORCE_LIGHT_JS,
) as demo:

    gr.ChatInterface(
        fn=respond,
        chatbot=custom_chatbot,
        textbox=custom_textbox,
        stop_btn=False,
        title=None,
    )

# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        ssr_mode=False,
        theme=custom_theme,
    )
