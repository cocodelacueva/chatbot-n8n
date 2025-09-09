import pandas as pd
import json
import re
from datetime import datetime
import openai
from docx import Document
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from dotenv import load_dotenv

#traer estos valores del .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EXCEL_PATH = os.getenv("EXCEL_PATH")
WORD_PATH = os.getenv("WORD_PATH")


class BookChatbotProcessor:
    def __init__(self, openai_api_key):
        """
        Procesador para crear base de conocimiento del chatbot de libros
        
        Args:
            openai_api_key: Tu clave de API de OpenAI
        """
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        self.knowledge_base = []
        
    def process_excel_catalog(self, excel_path, sheet_name=None):
        """
        Procesa el catálogo de libros desde Excel
        
        Args:
            excel_path: Ruta al archivo Excel
            sheet_name: Nombre de la hoja (opcional)
        """
        print("📚 Procesando catálogo de libros...")
        
        # Leer Excel
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # Normalizar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()
        expected_columns = ['título', 'autor', 'editorial', 'país', 'precio', 'stock']
        
        # Mapear posibles variaciones de nombres
        column_mapping = {
            'titulo': 'título',
            'title': 'título',
            'author': 'autor',
            'publisher': 'editorial',
            'country': 'país',
            'pais': 'país',
            'price': 'precio',
            'stock': 'stock',
            'cantidad': 'stock'
        }
        
        # Aplicar mapeo
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Verificar columnas necesarias
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            print(f"⚠️  Columnas faltantes: {missing_cols}")
            print(f"📋 Columnas disponibles: {list(df.columns)}")
        
        # Procesar cada libro
        for _, row in df.iterrows():
            book_info = {
                'tipo': 'catalogo',
                'título': str(row.get('título', 'No disponible')),
                'autor': str(row.get('autor', 'No disponible')),
                'editorial': str(row.get('editorial', 'No disponible')),
                'país': str(row.get('país', 'No disponible')),
                'precio': str(row.get('precio', 'No disponible')),
                'stock': str(row.get('stock', 'No disponible'))
            }
            
            # Crear texto descriptivo para embedding
            disponibilidad = "disponible" if str(row.get('stock', '0')).replace('.0', '') != '0' else "sin stock"
            
            text_content = f"""
            Libro: {book_info['título']}
            Autor: {book_info['autor']}
            Editorial: {book_info['editorial']}
            País: {book_info['país']}
            Precio: ${book_info['precio']}
            Estado: {disponibilidad}
            Tipo: Información de catálogo de libro
            """.strip()
            
            self.knowledge_base.append({
                'content': text_content,
                'metadata': book_info,
                'embedding': None
            })
        
        print(f"✅ Procesados {len(df)} libros del catálogo")
    
    def process_whatsapp_conversations(self, word_path):
        """
        Procesa conversaciones de WhatsApp desde documento Word
        
        Args:
            word_path: Ruta al archivo Word con conversaciones
        """
        print("💬 Procesando conversaciones de WhatsApp...")
        
        # Leer documento Word
        doc = Document(word_path)
        full_text = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                full_text.append(paragraph.text.strip())
        
        content = '\n'.join(full_text)
        
        # Dividir en conversaciones (buscar patrones comunes)
        conversations = self._split_conversations(content)
        
        for i, conversation in enumerate(conversations):
            if len(conversation.strip()) > 50:  # Filtrar conversaciones muy cortas
                
                # Extraer temas relevantes
                topics = self._extract_topics_from_conversation(conversation)
                
                conv_info = {
                    'tipo': 'conversacion',
                    'numero': i + 1,
                    'temas': topics,
                    'fecha': 'histórica'
                }
                
                self.knowledge_base.append({
                    'content': f"Conversación sobre libros:\n{conversation}",
                    'metadata': conv_info,
                    'embedding': None
                })
        
        print(f"✅ Procesadas {len(conversations)} conversaciones")
    
    def _split_conversations(self, content):
        """Divide el contenido en conversaciones individuales"""
        # Patrones comunes para dividir conversaciones
        patterns = [
            r'\n\s*\n\s*\n',  # Múltiples saltos de línea
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # Fechas
            r'\[\d{1,2}:\d{2}\]',  # Timestamps [HH:MM]
            r'---+',  # Separadores con guiones
        ]
        
        # Usar el patrón más efectivo
        for pattern in patterns:
            splits = re.split(pattern, content)
            if len(splits) > 1:
                return [split.strip() for split in splits if split.strip()]
        
        # Si no hay patrones claros, dividir por párrafos largos
        paragraphs = content.split('\n\n')
        conversations = []
        current_conv = []
        
        for paragraph in paragraphs:
            current_conv.append(paragraph)
            if len('\n'.join(current_conv)) > 500:  # Aprox 500 caracteres por conversación
                conversations.append('\n'.join(current_conv))
                current_conv = []
        
        if current_conv:
            conversations.append('\n'.join(current_conv))
        
        return conversations
    
    def _extract_topics_from_conversation(self, conversation):
        """Extrae temas relevantes de una conversación"""
        # Palabras clave relacionadas con libros
        book_keywords = ['libro', 'autor', 'novela', 'cuento', 'poesía', 'editorial', 
                        'leer', 'lectura', 'recomend', 'título', 'historia', 'narrativa']
        
        topics = []
        conversation_lower = conversation.lower()
        
        for keyword in book_keywords:
            if keyword in conversation_lower:
                topics.append(keyword)
        
        return list(set(topics))  # Eliminar duplicados
    
    def create_embeddings(self):
        """Crea embeddings para toda la base de conocimiento"""
        print("🧠 Creando embeddings...")
        
        for i, item in enumerate(self.knowledge_base):
            try:
                response = openai.Embedding.create(
                    model="text-embedding-ada-002",
                    input=item['content']
                )
                item['embedding'] = response['data'][0]['embedding']
                
                if (i + 1) % 10 == 0:
                    print(f"   Progreso: {i + 1}/{len(self.knowledge_base)}")
                    
            except Exception as e:
                print(f"❌ Error creando embedding {i}: {e}")
                item['embedding'] = [0.0] * 1536  # Embedding vacío como fallback
        
        print("✅ Embeddings creados")
    
    def save_knowledge_base(self, filename='knowledge_base.pkl'):
        """Guarda la base de conocimiento procesada"""
        with open(filename, 'wb') as f:
            pickle.dump(self.knowledge_base, f)
        print(f"💾 Base de conocimiento guardada en {filename}")
    
    def create_simple_search_function(self, output_file='search_function.py'):
        """Crea función de búsqueda simple para usar en n8n"""
        search_code = '''
import pickle
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class BookKnowledgeSearch:
    def __init__(self, knowledge_base_path, openai_api_key):
        """
        Inicializa el buscador de conocimiento
        """
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # Cargar base de conocimiento
        with open(knowledge_base_path, 'rb') as f:
            self.knowledge_base = pickle.load(f)
    
    def search_relevant_content(self, query, top_k=3):
        """
        Busca contenido relevante para una consulta
        
        Args:
            query: Pregunta del usuario
            top_k: Número de resultados a retornar
            
        Returns:
            Lista de contenidos relevantes
        """
        # Crear embedding de la consulta
        query_response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_embedding = query_response['data'][0]['embedding']
        
        # Calcular similitudes
        similarities = []
        for item in self.knowledge_base:
            if item['embedding']:
                similarity = cosine_similarity(
                    [query_embedding], 
                    [item['embedding']]
                )[0][0]
                similarities.append((similarity, item))
        
        # Ordenar por similitud
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        # Retornar top_k resultados
        results = []
        for score, item in similarities[:top_k]:
            results.append({
                'content': item['content'],
                'metadata': item['metadata'],
                'score': float(score)
            })
        
        return results

# Función para usar en n8n (HTTP endpoint)
def search_books(query, openai_api_key, knowledge_base_path='knowledge_base.pkl'):
    """
    Función simple para búsqueda (para usar en n8n como función personalizada)
    """
    searcher = BookKnowledgeSearch(knowledge_base_path, openai_api_key)
    results = searcher.search_relevant_content(query)
    
    # Formatear para usar como contexto
    context_parts = []
    for result in results:
        context_parts.append(result['content'])
    
    return "\\n---\\n".join(context_parts)
'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(search_code)
        
        print(f"🔍 Función de búsqueda creada en {output_file}")

def main():
    """Función principal para procesar documentos"""
    print("🚀 Iniciando procesamiento de documentos para chatbot de libros")
    
    # Configuración
    OPENAI_API_KEY = "tu-api-key-aqui"  # ¡CAMBIAR POR TU API KEY!
    EXCEL_PATH = "catalogo_libros.xlsx"  # Ruta a tu Excel
    WORD_PATH = "conversaciones_whatsapp.docx"  # Ruta a tu Word
    
    # Inicializar procesador
    processor = BookChatbotProcessor(OPENAI_API_KEY)
    
    # Procesar documentos
    try:
        processor.process_excel_catalog(EXCEL_PATH)
        processor.process_whatsapp_conversations(WORD_PATH)
        
        # Crear embeddings
        processor.create_embeddings()
        
        # Guardar base de conocimiento
        processor.save_knowledge_base()
        
        # Crear función de búsqueda
        processor.create_simple_search_function()
        
        print("\n✅ ¡Procesamiento completado!")
        print("📁 Archivos generados:")
        print("   - knowledge_base.pkl (base de conocimiento)")
        print("   - search_function.py (función de búsqueda)")
        
    except FileNotFoundError as e:
        print(f"❌ Error: No se encontró el archivo {e}")
        print("📝 Asegúrate de que los archivos estén en la misma carpeta")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
