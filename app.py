import os
import csv
from groq import Groq

# 1. Inicializar el cliente de Groq leyendo la variable de entorno del sistema
# Si estás usando Windows, a veces es necesario pasarle la clave directamente si no lee el archivo .env:
# client = Groq(api_key="tu_gsk_completa_aqui")
client = Groq()

def obtener_contexto_local(pregunta_usuario, ruta_csv="faqs.csv"):
    """Busca palabras clave de forma simple dentro del archivo CSV de la alcaldía."""
    pregunta_usuario = pregunta_usuario.lower()
    contexto = ""
    
    try:
        with open(ruta_csv, mode='r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                # Comprobamos si alguna palabra de la pregunta coincide con las FAQs
                palabras_usuario = set(pregunta_usuario.split())
                palabras_faq = set(fila['pregunta'].lower().split())
                
                if palabras_usuario.intersection(palabras_faq):
                    contexto += f"Pregunta frecuente: {fila['pregunta']}\nRespuesta oficial: {fila['respuesta']}\n\n"
    except FileNotFoundError:
        print("⚠️ Nota: Archivo faqs.csv no encontrado. Continuando sin contexto local.")
        
    return contexto if contexto else "No hay información específica en el manual de procesos locales."

def preguntar_a_llama(pregunta, contexto):
    """Envía la pregunta y el contexto de la alcaldía al modelo Llama 3 en la nube."""
    
    prompt_sistema = (
   "Eres un chatbot de atención al ciudadano para una alcaldía en Colombia. "
        "Tu única fuente de verdad es el 'Contexto de la alcaldía' provisto abajo. "
        "Analiza el contexto minuciosamente. Si el contexto responde la pregunta (como los días u horarios), "
        "ENTREGA la información completa que aparezca allí de forma amable y clara. "
        "Solo si el contexto no dice NADA sobre el tema, di que no posees la información."
    )
    
    prompt_usuario = f"Contexto de la alcaldía:\n{contexto}\n\nPregunta del ciudadano: {pregunta}"
    
    try:
        # Usamos el modelo llama3-8b-8192 que es gratuito, ultra rápido y potente
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",

            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.2 # Temperatura baja para evitar respuestas inventadas
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error de conexión con el motor de IA: {e}"

# --- Flujo Principal de Consola ---
if __name__ == "__main__":
    print("🤖 [Asistente Virtual Alcaldía] En línea. Escribe 'salir' para terminar.\n")
    
    while True:
        entrada = input("Ciudadano: ")
        if entrada.lower() == 'salir':
            print("Bot: Que tenga un excelente día. ¡Hasta luego!")
            break
            
        # 1. Buscar si el trámite existe en nuestro CSV
        contexto_encontrado = obtener_contexto_local(entrada)
        
        # 2. Procesar con Inteligencia Artificial enviándole las reglas de juego
        respuesta_ia = preguntar_a_llama(entrada, contexto_encontrado)
        
        print(f"Bot: {respuesta_ia}\n")
