// Procesar datos de Google Sheets con filtro estricto de stock

// Obtener datos de entrada
const inputData = $input.first().json;

// Obtener mensaje del usuario
const userMessage = (inputData.body?.message?.text || 
                    inputData.message?.text || 
                    "consulta general").toLowerCase().trim();

// Obtener datos de Google Sheets
const catalogData = $('2. Leer Catálogo (Google Sheets)').all();

console.log('🔍 Mensaje:', userMessage);
console.log('📊 Items del catálogo:', catalogData.length);

// Debug: mostrar algunos items del catálogo
catalogData.slice(0, 3).forEach((item, index) => {
  console.log(`📖 Item ${index}:`, JSON.stringify(item.json, null, 2));
});

// Función mejorada para buscar libros con stock
function searchAvailableBooks(query, catalog) {
  const results = [];
  const queryWords = query.split(' ').filter(word => word.length > 2);
  
  console.log('🔎 Palabras de búsqueda:', queryWords);

  catalog.forEach((item, index) => {
    if (!item?.json) {
      console.log(`⚠️ Item ${index} sin datos JSON`);
      return;
    }

    const book = item.json;
    
    // Debug: mostrar estructura del libro
    if (index < 2) {
      console.log(`📚 Libro ${index}:`, {
        titulo: book['Título'] || book['titulo'] || book['Title'],
        stock: book['Stock'] || book['stock'],
        stockRaw: typeof (book['Stock'] || book['stock'])
      });
    }

    // FILTRO ESTRICTO DE STOCK PRIMERO
    const stockValue = book['Stock'] || book['stock'] || '0';
    const stockString = String(stockValue).replace('.0', '').trim().toLowerCase();
    
    // Verificar si tiene stock disponible
    const hasStock = stockString !== '0' && 
                    stockString !== '' && 
                    stockString !== 'no' && 
                    stockString !== 'agotado' && 
                    stockString !== 'sin stock' &&
                    Number(stockString) > 0;

    // Solo procesar si tiene stock
    if (!hasStock) {
      return; // Saltar libros sin stock
    }

    let relevanceScore = 0;
    
    // Buscar coincidencias solo si tiene stock
    const title = String(book['Título'] || book['titulo'] || book['Title'] || '').toLowerCase();
    const author = String(book['Autor'] || book['autor'] || book['Author'] || '').toLowerCase();
    const editorial = String(book['Editorial'] || book['editorial'] || '').toLowerCase();

    // Coincidencia exacta en título (alta prioridad)
    queryWords.forEach(word => {
      if (title.includes(word)) relevanceScore += 5;
      if (author.includes(word)) relevanceScore += 3;
      if (editorial.includes(word)) relevanceScore += 1;
    });

    // Solo agregar si hay coincidencias Y tiene stock
    if (relevanceScore > 0) {
      results.push({
        titulo: book['Título'] || book['titulo'] || book['Title'] || 'Sin título',
        autor: book['Autor'] || book['autor'] || book['Author'] || 'Sin autor',
        editorial: book['Editorial'] || book['editorial'] || 'Sin editorial',
        pais: book['País'] || book['Pais'] || book['pais'] || 'Sin país',
        precio: book['Precio'] || book['precio'] || 'Consultar',
        stock: stockString,
        disponible: true, // Solo agregamos si tiene stock
        relevanceScore: relevanceScore
      });
    }
  });

  console.log(`📚 Libros con stock encontrados: ${results.length}`);
  
  return results.sort((a, b) => b.relevanceScore - a.relevanceScore).slice(0, 5);
}

// Función para obtener libros disponibles (sin búsqueda específica)
function getGeneralAvailableBooks(catalog, limit = 3) {
  const available = [];
  
  catalog.forEach((item, index) => {
    if (!item?.json || available.length >= limit) return;
    
    const book = item.json;
    const stockValue = book['Stock'] || book['stock'] || '0';
    const stockString = String(stockValue).replace('.0', '').trim().toLowerCase();
    
    const hasStock = stockString !== '0' && 
                    stockString !== '' && 
                    stockString !== 'no' && 
                    stockString !== 'agotado' &&
                    Number(stockString) > 0;
    
    if (hasStock) {
      available.push({
        titulo: book['Título'] || book['titulo'] || book['Title'] || 'Sin título',
        autor: book['Autor'] || book['autor'] || book['Author'] || 'Sin autor',
        precio: book['Precio'] || book['precio'] || 'Consultar',
        stock: stockString,
        disponible: true
      });
    }
  });
  
  console.log(`📖 Libros disponibles en general: ${available.length}`);
  return available;
}

// Realizar búsqueda
const searchResults = searchAvailableBooks(userMessage, catalogData);
const fallbackBooks = searchResults.length === 0 ? getGeneralAvailableBooks(catalogData) : [];

const booksToShow = searchResults.length > 0 ? searchResults : fallbackBooks;

console.log(`✅ Total libros a mostrar: ${booksToShow.length}`);

// Crear contexto MUY ESPECÍFICO para evitar alucinaciones
let context = "";

if (booksToShow.length > 0) {
  context = "LIBROS DISPONIBLES EN NUESTRO CATÁLOGO (STOCK CONFIRMADO):\\n\\n";
  
  booksToShow.forEach((book, index) => {
    context += `${index + 1}. 📚 TÍTULO: ${book.titulo}\\n`;
    context += `   👤 AUTOR: ${book.autor}\\n`;
    context += `   💰 PRECIO: $${book.precio}\\n`;
    context += `   📦 STOCK DISPONIBLE: ${book.stock} unidades\\n`;
    context += `   ✅ ESTADO: DISPONIBLE PARA COMPRA\\n\\n`;
  });
  
  context += "INSTRUCCIONES IMPORTANTES:\\n";
  context += "- SOLO recomienda libros de esta lista exacta\\n";
  context += "- NUNCA inventes títulos o autores\\n";
  context += "- Si no hay libros específicos para la consulta, ofrece los disponibles\\n";
  context += "- SIEMPRE menciona que verificaste el stock en tiempo real\\n";
} else {
  context = "ESTADO ACTUAL DEL CATÁLOGO:\\n\\n";
  context += "❌ No hay libros disponibles en stock en este momento para la consulta específica.\\n";
  context += "📞 Recomendamos contactar directamente para consultar próximas llegadas.\\n\\n";
  context += "INSTRUCCIÓN: Informa que no hay stock disponible y sugiere contactar para más información.\\n";
}

// Determinar tipo de consulta
let queryType = 'general';
if (userMessage.includes('precio') || userMessage.includes('cuesta')) queryType = 'precio';
else if (userMessage.includes('stock') || userMessage.includes('disponible')) queryType = 'stock';
else if (userMessage.includes('autor')) queryType = 'autor';
else if (userMessage.includes('recomend')) queryType = 'recomendacion';

const result = {
  userMessage: inputData.body?.message?.text || inputData.message?.text || "consulta general",
  context: context,
  queryType: queryType,
  foundBooks: booksToShow.length,
  books: booksToShow,
  hasStock: booksToShow.length > 0
};

console.log('📊 Resultado final:', {
  foundBooks: result.foundBooks,
  hasStock: result.hasStock,
  queryType: result.queryType
});

return [{ json: result }];