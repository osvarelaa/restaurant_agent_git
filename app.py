from flask import Flask, render_template, request, jsonify
import json
from restaurant_agent import RestaurantAgent
import openai

import os
openai.api_key = os.environ.get("OPENAI_API_KEY")

app = Flask(__name__)
agent = RestaurantAgent()
openai.api_key = "TU_API_KEY"  # Tu API Key OpenAI

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/instruccion", methods=["POST"])
def instruccion():
    user_input = request.form["instruccion"]
    # Llama al LLM para interpretar la instrucción
    prompt = f"""Eres un agente de restaurante. Recibes instrucciones como: "{user_input}".
El contexto es: Reservaciones y pedidos de restaurante.
Devuelve un JSON con los campos:
- accion: 'consultar', 'insertar', 'actualizar', 'borrar'
- entidad: 'reservacion', 'pedido', 'producto'
- parametros: los parámetros relevantes (nombre, fecha, mesa, productos, etc.)
Ejemplo de respuesta:
{{"accion":"insertar","entidad":"reservacion","parametros":{{"nombre":"Juan","telefono":"5544332211","fecha":"2025-08-20","hora":"19:30","mesa":2}}}}
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=300
    )
    action_json = response.choices[0].message["content"]

    try:
        action_dict = json.loads(action_json)
        accion = action_dict.get('accion')
        entidad = action_dict.get('entidad')
        parametros = action_dict.get('parametros', {})
    except Exception as e:
        return jsonify({"respuesta": "No se pudo interpretar la instrucción."})

    # Ejecuta la acción correspondiente
    def ejecutar_accion(agent, accion, entidad, parametros):
        try:
            if accion == "consultar":
                if entidad == "reservacion":
                    return agent.consultar_reservaciones(parametros)
                elif entidad == "producto":
                    return agent.consultar_productos(parametros)
                elif entidad == "pedido":
                    return agent.consultar_pedidos(parametros)
            elif accion == "insertar":
                if entidad == "reservacion":
                    return agent.crear_reservacion(**parametros)
                elif entidad == "producto":
                    return agent.agregar_producto(**parametros)
                elif entidad == "pedido":
                    return agent.crear_pedido(**parametros)
            elif accion == "actualizar":
                id = parametros.pop('id')
                if entidad == "reservacion":
                    return agent.actualizar_reservacion(id, parametros)
                elif entidad == "producto":
                    return agent.actualizar_producto(id, parametros)
                elif entidad == "pedido":
                    return agent.actualizar_pedido(id, parametros)
            elif accion == "borrar":
                id = parametros['id']
                if entidad == "reservacion":
                    return agent.borrar_reservacion(id)
                elif entidad == "producto":
                    return agent.borrar_producto(id)
                elif entidad == "pedido":
                    return agent.borrar_pedido(id)
            return "Acción no reconocida"
        except Exception as e:
            return f"Error: {str(e)}"

    resultado = ejecutar_accion(agent, accion, entidad, parametros)
    return jsonify({"respuesta": str(resultado)})

if __name__ == "__main__":
    agent.insertar_datos_demo()
    app.run(debug=True)
