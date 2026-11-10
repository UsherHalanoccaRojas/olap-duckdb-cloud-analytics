"""
Script para generar el archivo comprimido ZIP de entrega oficial:
AG02_IN_U02_HALANOCCA_ROJAS_ENTREGA.zip
"""

import os
import zipfile

OUTPUT_ZIP = "AG02_IN_U02_HALANOCCA_ROJAS_ENTREGA.zip"

def create_delivery_zip():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, OUTPUT_ZIP)
    
    # Exclusiones
    exclude_dirs = {'.git', 'venv', 'env', '.venv', '__pycache__'}
    exclude_exts = {'.pyc', '.pyo', '.zip'}
    
    print(f"[*] Comprimiendo archivos para entrega en {OUTPUT_ZIP}...")
    file_count = 0
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Filtrar directorios
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in exclude_exts or file == OUTPUT_ZIP:
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                
                zipf.write(full_path, rel_path)
                file_count += 1
                print(f"  + Agregado: {rel_path}")

    zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"[+] Archivo ZIP generado exitosamente: {OUTPUT_ZIP}")
    print(f"[+] Total archivos incluidos: {file_count} | Tamaño final: {zip_size_mb:.2f} MB")

if __name__ == "__main__":
    create_delivery_zip()
