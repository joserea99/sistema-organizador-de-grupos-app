from io import BytesIO

def generar_plantilla_excel_bytes():
    """Genera la plantilla de Excel para importación de grupo en memoria y retorna los BytesIO"""
    try:
        import pandas as pd
        
        # Crear datos de ejemplo
        data = {
            'Nombre': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Pedro Sánchez'],
            'Dirección': ['Calle 123 Col. Centro', 'Av. Principal 456', 'Blvd. Sur 789', 'Col. Norte 321', 'Calle Centro 654'],
            'Teléfono': ['555-0123', '555-0124', '555-0125', '555-0126', '555-0127'],
            'Email': ['juan@example.com', 'maria@example.com', '', 'ana@example.com', ''],
            'Edad': [35, 28, 42, 31, 29],
            'Estado Civil': ['Casado', 'Soltera', 'Casado', 'Casada', 'Soltero'],
            'Num Hijos': [2, 0, 3, 1, 0],
            'Edades Hijos': ['5, 8', '', '10, 12, 15', '7', ''],
            'Nombre Cónyuge': ['María Pérez', '', 'Ana López', 'Roberto Martínez', ''],
            'Edad Cónyuge': [32, '', 38, 33, ''],
            'Teléfono Cónyuge': ['555-0130', '', '555-0131', '555-0132', ''],
            'Email Cónyuge': ['maria.perez@example.com', '', 'ana.lopez@example.com', '', ''],
            'Trabajo Cónyuge': ['Maestra', '', 'Doctora', 'Ingeniero', ''],
            'Fecha Matrimonio': ['2018-06-15', '', '2005-03-20', '2015-09-10', '']
        }
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Plantilla', index=False)
            
            # Ajustar ancho de columnas
            workbook = writer.book
            worksheet = writer.sheets['Plantilla']
            
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output, 'excel'
        
    except ImportError:
        # Fallback a CSV si pandas no está disponible
        contenido_csv = """Nombre,Dirección,Teléfono,Email,Edad,Estado Civil,Num Hijos,Edades Hijos,Nombre Cónyuge,Edad Cónyuge,Teléfono Cónyuge,Email Cónyuge,Trabajo Cónyuge,Fecha Matrimonio
Juan Pérez,Calle 123 Col. Centro,555-0123,juan@example.com,35,Casado,2,"5,8",María Pérez,32,555-0130,maria.perez@example.com,Maestra,2018-06-15
María García,Av. Principal 456,555-0124,maria@example.com,28,Soltera,0,,,,,,,
Carlos López,Blvd. Sur 789,555-0125,,42,Casado,3,"10,12,15",Ana López,38,555-0131,ana.lopez@example.com,Doctora,2005-03-20
Ana Martínez,Col. Norte 321,555-0126,ana@example.com,31,Casada,1,"7",Roberto Martínez,33,555-0132,,Ingeniero,2015-09-10
Pedro Sánchez,Calle Centro 654,555-0127,,29,Soltero,0,,,,,,,"""
        
        output = BytesIO()
        output.write(contenido_csv.encode('utf-8'))
        output.seek(0)
        return output, 'csv'
