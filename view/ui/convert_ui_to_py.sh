#!/bin/bash

# Script para convertir archivos UI de PyQt6 a Python en el paquete view/windows
# Debe ejecutarse desde view/ui

echo "Convirtiendo archivos UI de PyQt6 a Python en el paquete view/windows..."

# Crear el directorio ../windows si no existe
mkdir -p ../windows

# Buscar archivos .ui en el directorio actual
ui_files=(*.ui)

if [ ! -e "${ui_files[0]}" ]; then
    echo "Error: No se encontraron archivos UI en el directorio actual."
    echo "Coloca tus archivos .ui aquí y ejecuta el script nuevamente."
    exit 1
fi

count=0

for ui_file in "${ui_files[@]}"; do
    base_name="${ui_file%.ui}"
    py_file="../windows/${base_name}.py"

    echo "Convirtiendo: $ui_file → $py_file"
    pyuic6 -o "$py_file" "$ui_file"

    if [ $? -eq 0 ]; then
        echo "✓ Conversión exitosa: $py_file"
        ((count++))
    else
        echo "✗ Error al convertir $ui_file"
    fi
done

echo "----------------------------------------"
echo "Conversión completada: $count archivo(s) convertido(s)."
echo "----------------------------------------"