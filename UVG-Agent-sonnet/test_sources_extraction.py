#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción automática de información
de descarga de PDFs usando el SDK de Nuclia.
Este script simula cómo el agente obtiene automáticamente URLs temporales
de descarga para archivos.
"""

import json
from app.agent import extract_sources_info

def test_extract_sources_from_response():
    """
    Prueba la extracción de fuentes y URLs de descarga usando el SDK de Nuclia.
    IMPORTANTE: Este test hace llamadas reales al SDK de Nuclia para obtener
    URLs temporales de descarga.
    """
    # Cargar el JSON de respuesta de ejemplo
    with open("response.json", "r", encoding="utf-8") as f:
        response_data = json.load(f)
    
    print("=" * 80)
    print("TEST: Extracción con SDK de Nuclia - URLs Temporales de Descarga")
    print("=" * 80)
    print("\n⚠️  NOTA: Este test hace llamadas reales a la API de Nuclia")
    print("    para obtener URLs temporales de descarga.\n")
    
    # Extraer sources (esto hará llamadas al SDK para archivos)
    sources = extract_sources_info(
        response_data,
        max_chunks=10,
        score_threshold=0.0
    )
    
    print(f"\n✅ Se extrajeron {len(sources)} fuentes\n")
    
    # Analizar cada fuente
    downloadable_count = 0
    link_count = 0
    
    for idx, source in enumerate(sources, 1):
        print(f"\n{'='*60}")
        print(f"Fuente #{idx}")
        print(f"{'='*60}")
        print(f"Título: {source.get('title')}")
        print(f"Tipo: {source.get('resource_type')}")
        print(f"Resource ID: {source.get('resource_id')}")
        print(f"Score: {source.get('score')}")
        if source.get('page'):
            print(f"Página: {source.get('page')}")
        
        if source.get('is_downloadable'):
            downloadable_count += 1
            file_info = source.get('file', {})
            print(f"\n📥 ARCHIVO DESCARGABLE (con URL temporal):")
            print(f"  - URL Temporal: {file_info.get('download_url')[:80]}...")
            print(f"  - Content Type: {file_info.get('content_type')}")
            print(f"  - Tamaño: {file_info.get('size')} bytes ({file_info.get('size', 0) / 1024:.2f} KB)")
            print(f"  - Nombre: {file_info.get('filename')}")
            print(f"  - File ID: {file_info.get('file_id')}")
            print(f"  - TTL: {file_info.get('ttl', 3600)} segundos")
            print(f"  - Es PDF: {'✅' if file_info.get('is_pdf') else '❌'}")
            print(f"  - Es Excel: {'✅' if file_info.get('is_excel') else '❌'}")
            
            # Validar que la URL es temporal (contiene token)
            if 'token' in file_info.get('download_url', '').lower():
                print(f"  ✅ URL contiene token temporal")
            else:
                print(f"  ℹ️  URL estándar (puede requerir autenticación)")
                
        elif source.get('resource_type') == 'application/stf-link':
            link_count += 1
            print(f"\n🔗 ENLACE WEB")
            print(f"  - URL: {source.get('url')}")
        else:
            print(f"\n📄 Otro tipo de recurso")
            print(f"  - URL: {source.get('url')}")
        
        # Mostrar extracto del texto
        text_preview = source.get('text', '')[:150].replace('\n', ' ')
        print(f"\n📝 Extracto:")
        print(f"   {text_preview}...")
    
    # Resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)
    print(f"Total de fuentes: {len(sources)}")
    print(f"Archivos descargables: {downloadable_count}")
    print(f"Enlaces web: {link_count}")
    print(f"Otros: {len(sources) - downloadable_count - link_count}")
    
    # Validación
    print("\n" + "=" * 80)
    print("✔️  VALIDACIÓN")
    print("=" * 80)
    
    all_downloadable_have_urls = all(
        source.get('file', {}).get('download_url') 
        for source in sources 
        if source.get('is_downloadable')
    )
    
    if all_downloadable_have_urls:
        print("✅ Todos los archivos descargables tienen download_url")
    else:
        print("❌ Algunos archivos descargables no tienen download_url")
    
    # Verificar que se obtuvieron URLs temporales
    temporal_urls = [
        source.get('file', {}).get('download_url')
        for source in sources
        if source.get('is_downloadable')
    ]
    
    if temporal_urls:
        print(f"✅ Se obtuvieron {len(temporal_urls)} URLs temporales de descarga")
        print(f"   TTL: 3600 segundos (1 hora)")
    
    # Mostrar ejemplo de uso
    print("\n" + "=" * 80)
    print("💡 EJEMPLO DE USO")
    print("=" * 80)
    
    for source in sources:
        if source.get('is_downloadable'):
            file_info = source.get('file', {})
            temporal_url = file_info.get('download_url')
            print(f"\nPara descargar: {source.get('title')}")
            print(f"\n1. URL Temporal (válida por 1 hora, no requiere auth):")
            print(f"   {temporal_url}")
            print(f"\n2. Esta URL puede usarse directamente desde el frontend:")
            print(f"   fetch('{temporal_url}')")
            print(f"     .then(r => r.blob())")
            print(f"     .then(blob => {{")
            print(f"       // Descargar archivo")
            print(f"     }})")
            break
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)
    
    return sources


if __name__ == "__main__":
    try:
        sources = test_extract_sources_from_response()
        print(f"\n🎉 Éxito: Se procesaron {len(sources)} fuentes correctamente")
        print(f"   Se obtuvieron URLs temporales usando el SDK de Nuclia")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

