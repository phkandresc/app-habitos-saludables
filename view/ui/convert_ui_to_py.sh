#!/bin/bash

# Script to convert PyQt6 UI files to Python files
# Usage: ./convert_ui_to_py.sh

echo "Converting PyQt6 UI files to Python..."

# Check if there are any .ui files in the current directory
ui_files=(*.ui)

if [ ! -e "${ui_files[0]}" ]; then
    echo "Error: No UI files found in current directory."
    echo "Please place your .ui files in this directory and run the script again."
    exit 1
fi

# Counter for successful conversions
count=0

# Process each UI file
for ui_file in "${ui_files[@]}"; do
    # Extract the base name without extension
    base_name="${ui_file%.ui}"
    
    # Set the output Python file name
    py_file="${base_name}.py"
    
    echo "Converting: $ui_file → $py_file"
    
    # Convert the UI file to Python
    pyuic6 -o "$py_file" "$ui_file"
    
    # Check if conversion was successful
    if [ $? -eq 0 ]; then
        echo "✓ Conversion successful: $py_file"
        ((count++))
    else
        echo "✗ Error converting $ui_file"
    fi
done

echo "----------------------------------------"
echo "Conversion completed: $count file(s) converted."
echo "----------------------------------------"

# Make the script executable after creating it
# Run: chmod +x convert_ui_to_py.sh

