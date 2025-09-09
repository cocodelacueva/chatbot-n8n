# 🤖 Configuración Completa del Chatbot de Libros

## 📋 **Requisitos Previos**

1. **Archivos necesarios:**
   - 📊 Excel con catálogo (columnas: Título, Autor, Editorial, País, Precio, Stock)
   - 📄 Documento Word con conversaciones de WhatsApp
   - 🔑 API Key de OpenAI

2. **Servicios externos:**
   - Cuenta en OpenAI
   - Proveedor de WhatsApp (Twilio recomendado)
   - n8n instalado

## 🚀 **Paso 1: Procesar tus Documentos**

### Instalación de dependencias Python:
```bash
pip install pandas openpyxl python-docx openai scikit-learn numpy pickle5
```

### Configurar el procesador:
1. Descarga el código del **Procesador de Documentos**
2. Coloca tus archivos en la misma carpeta:
   - `catalogo_libros.xlsx`
   - `conversaciones_whatsapp.docx`
3. Edita el archivo y cambia:
   ```python
   OPENAI_API_KEY = "tu-api-key-de-openai-aqui"
   ```
4. Ejecuta: `python procesador.py`

### Resultado:
- 📁 `knowledge_base.pkl` (base de conocimiento)
- 🔍 `search_function.py` (función de búsqueda)

## 🔧 **Paso 2: Configurar n8n**

### Importar workflow:
1. Copia el JSON del **Workflow n8n Completo**
2. En n8n: `Settings` → `Import from JSON`
3. Pega el contenido

### Configurar credenciales:

#### OpenAI API:
1. `Settings` → `Credentials` → `Add Credential`
2. Buscar "OpenAI"
3. Agregar tu API Key

#### Twilio (para WhatsApp):
1. `Settings` → `Credentials` → `Add Credential`
2. Buscar "HTTP Basic Auth"
3. Username: Tu Twilio Account SID
4. Password: Tu Twilio Auth Token

### Modificar nodos específicos:

#### Nodo 5 (Enviar WhatsApp):
Cambiar en la URL:
```
https://api.twilio.com/2010-04-01/Accounts/TU_ACCOUNT_SID/Messages.json
```

En el campo "From":
```
whatsapp:+TU_NUMERO_TWILIO
```

#### Nodo 3 (Base de Conocimiento):
Para usar tu base real, reemplazar el código JavaScript por:

```javascript
// Cargar tu base de conocimiento real
const fs = require('fs');
const pickle = require('pickle'); // Necesitarás un módulo de pickle para JS

// Aquí cargarías tu knowledge_base.pkl
// Por ahora usa la búsqueda simplificada del código actual
```

## 📱 **Paso 3: Configurar WhatsApp**

### Con Twilio:
1. Ve a [Twilio Console](https://console.twilio.com/)
2. `Messaging` → `Try it out` → `Send a WhatsApp message`
3. Configura el webhook URL: `https://tu-n8n-url/webhook/webhook-whatsapp`

### Con 360Dialog:
1. Configura webhook en tu panel 360Dialog
2. URL: `https://tu-n8n-url/webhook/webhook-whatsapp`

## 🧪 **Paso 4: Pruebas**

### Probar workflow interno:
1. Usar nodo "Datos de Prueba"
2. Ejecutar workflow manualmente
3. Verificar cada paso

### Probar WhatsApp:
1. Envía mensaje a tu número de WhatsApp
2. Verifica logs en n8n
3. Confirma respuesta del bot

## 🔄 **Mejoras Opcionales**

### Para base de conocimiento avanzada:
- Usar Pinecone o Weaviate como base vectorial
- Implementar caché de embeddings
- Agregar análisis de sentimientos

### Para respuestas mejoradas:
- Usar GPT-4 en lugar de GPT-3.5
- Implementar memory de conversación
- Agregar templates de respuesta

## ❌ **Solución de Problemas Comunes**

### Error en embeddings:
- Verificar API Key de OpenAI
- Verificar formato del mensaje entrante

### No recibe mensajes de WhatsApp:
- Verificar URL del webhook
- Comprobar configuración en proveedor
- Revisar logs de n8n

### Respuestas incorrectas:
- Verificar procesamiento de documentos
- Ajustar prompt del sistema
- Mejorar base de conocimiento

## 💡 **Consejos Importantes**

1. **Seguridad**: No expongas tus API keys en el código
2. **Escalabilidad**: Para alto volumen, considera usar base vectorial externa
3. **Costos**: Monitorea uso de OpenAI API
4. **Backup**: Guarda backup de tu `knowledge_base.pkl`

## 🎯 **Resultado Final**

Tu chatbot podrá:
- ✅ Responder consultas sobre libros del catálogo
- ✅ Dar precios y disponibilidad
- ✅ Hacer recomendaciones basadas en conversaciones pasadas
- ✅ Mantener contexto relevante
- ✅ Funcionar 24/7 vía WhatsApp

---

**¿Necesitas ayuda con algún paso específico?** ¡Pregúntame!