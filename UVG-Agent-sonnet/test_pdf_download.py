#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema obtiene automáticamente 
la información de PDFs desde los recursos de Nuclia.
"""

from app.agent import ask_agent
import json

def test_pdf_retrieval():
    """Prueba que el sistema obtiene automáticamente información de PDFs"""
    
    # Hacer una consulta que probablemente devuelva PDFs
    question = "¿Qué información tienes sobre documentos?"
    
    print(f"🔍 Consultando: {question}\n")
    
    try:
        result = ask_agent(
            question=question,
            size=10,
            max_chunks=5,
            use_semantic=True,
            min_score=0.0
        )
        
        print(f"✅ Respuesta recibida\n")
        print(f"📝 Respuesta: {result['answer'][:200]}...\n")
        
        # Verificar si hay PDFs en las fuentes
        pdf_sources = [s for s in result['sources'] if s.get('is_pdf')]
        
        if pdf_sources:
            print(f"📄 Se encontraron {len(pdf_sources)} PDFs:\n")
            for source in pdf_sources:
                print(f"  - {source['title']}")
                print(f"    Resource ID: {source['resource_id']}")
                if 'pdf' in source:
                    pdf_info = source['pdf']
                    print(f"    Download URL: {pdf_info['download_url']}")
                    print(f"    Content Type: {pdf_info['content_type']}")
                    print(f"    Size: {pdf_info['size']} bytes")
                    print(f"    Filename: {pdf_info['filename']}")
                print()
        else:
            print("ℹ️  No se encontraron PDFs en los resultados\n")
        
        # Mostrar todas las fuentes
        print(f"📚 Total de fuentes: {len(result['sources'])}\n")
        for source in result['sources']:
            print(f"  {source['id']}. {source['title']}")
            print(f"     Score: {source['score']}, Page: {source.get('page', 'N/A')}")
            print(f"     PDF: {'Sí' if source.get('is_pdf') else 'No'}")
            print()
        
        # Guardar resultado completo para inspección
        with open('test_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("💾 Resultado completo guardado en test_result.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pdf_retrieval()
