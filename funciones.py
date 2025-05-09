
import pandas as pd 

COLUMNAS_FINALES = ["NOM_MUN","P_0A4","P_0A4_F","P_0A4_M","P_5A9","P_5A9_F","P_5A9_M","P_10A14","P_10A14_F","P_10A14_M","P_15A19","P_15A19_F",
            "P_15A19_M","P_20A24","P_20A24_F","P_20A24_M","P_25A29","P_25A29_F","P_25A29_M","P_30A34","P_30A34_F","P_30A34_M",
            "P_35A39","P_35A39_F","P_35A39_M","P_40A44","P_40A44_F","P_40A44_M","P_45A49","P_45A49_F","P_45A49_M","P_50A54",
            "P_50A54_F","P_50A54_M","P_55A59","P_55A59_F","P_55A59_M","P_60A64","P_60A64_F","P_60A64_M","P_65A69","P_65A69_F",
            "P_65A69_M","P_70A74","P_70A74_F","P_70A74_M","P_75A79","P_75A79_F","P_75A79_M","P_80A84","P_80A84_F","P_80A84_M",
            "P_85YMAS","P_85YMAS_F","P_85YMAS_M"]



def obtener_datos():
    """
    Función para obtener datos de un archivo parquet y procesarlos."""
    try:
        df_inegi = pd.read_parquet('assets/docs/conjunto_de_datos_iter_13CSV20.parquet')
        if df_inegi.empty:
            raise ValueError("El DataFrame está vacío o no se leyo correctamente.")
        
        df_inegi = df_inegi.iloc[3:]
        patron_excluir = 'Localidades de una vivienda|Localidades de dos viviendas|Total del Municipio'
        df_inegi = df_inegi[~df_inegi['NOM_LOC'].str.contains(patron_excluir, case=False, na=False)]
        columnas_a_eliminar = ['ENTIDAD', 'NOM_ENT', 'MUN', 'LOC', 'NOM_LOC', 'LONGITUD', 'LATITUD', 'ALTITUD']
        df_inegi_pob = df_inegi.drop(columns=columnas_a_eliminar)
        cols_numericas = df_inegi_pob.columns.difference(['NOM_MUN'])
        df_inegi_pob[cols_numericas] = df_inegi_pob[cols_numericas].apply(pd.to_numeric, errors='coerce')
        df_inegi_pob = df_inegi_pob[COLUMNAS_FINALES]
        df_agrupado = df_inegi_pob.groupby('NOM_MUN').sum()
        municipios = df_agrupado.index.tolist()
        return df_agrupado, municipios
    
    except FileNotFoundError:
        print("El archivo no se encontró.")
        return None, None
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return None, None


def auxiliares_salud():
    """
    Función para obtener el número total de auxiliares de salud por municipio,
    filtrado por unidades con CLUES que empiezan por 'HGSSA'.

    Returns:
        pd.DataFrame: Con columnas ['Nombre Municipio Loc', 'Auxiliar de Salud'].
                     Retorna DataFrame vacío si hay errores.
    """
    try:
        # Cargar datos
        df_aux = pd.read_parquet('assets/docs/Reporte Auxiliares, Casas de Salud y Parteras.parquet')
        
        # Filtrar unidades SSA y limpiar datos
        unidades_ssa = df_aux[df_aux['CLUES'].astype(str).str.startswith('HGSSA')].copy()
        unidades_ssa['Auxiliar de Salud'] = unidades_ssa['Auxiliar de Salud'].fillna(0)  # Si es numérico
        
        # Agrupar y sumar
        total_auxiliares = unidades_ssa.groupby('Nombre Municipio Loc', as_index=False)['Auxiliar de Salud'].sum()
        
        return total_auxiliares

    except FileNotFoundError:
        print("Error: El archivo no se encontró.")
        return pd.DataFrame()  # Retorno consistente
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return pd.DataFrame()
    

def casas_salud():
    """
    Función para obtener el número total de casas de salud por municipio y tipo,
    filtrado por unidades con CLUES que empiezan por 'HGSSA'.

    Returns:
        pd.DataFrame: Con columnas:
            - 'Nombre Municipio Loc': Nombre del municipio.
            - Otras columnas dinámicas por cada tipo de casa de salud.
            Los valores representan el conteo de cada tipo por municipio.
            Retorna DataFrame vacío si hay errores.
    """
    try:
        # Cargar datos
        doc = pd.read_parquet('assets/docs/Reporte Auxiliares, Casas de Salud y Parteras.parquet')
        
        # Verificar si el DataFrame está vacío
        if doc.empty:
            print("Advertencia: El archivo está vacío.")
            return pd.DataFrame()

        # Filtrar y limpiar datos
        casas = doc[doc['CLUES'].astype(str).str.startswith('HGSSA')].copy()
        cols = ['Nombre Municipio Loc', 'Tipo Casa Salud']
        casas = casas[cols].dropna(subset=["Tipo Casa Salud"])
        
        # Verificar si hay datos después del filtrado
        if casas.empty:
            print("Advertencia: No hay datos válidos después del filtrado.")
            return pd.DataFrame()

        # Crear pivot table
        casas_salud_pivot = casas.pivot_table(
            index='Nombre Municipio Loc',
            columns='Tipo Casa Salud',
            aggfunc='size',
            fill_value=0
        ).reset_index()

        return casas_salud_pivot

    except FileNotFoundError:
        print("Error: El archivo no se encontró.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return pd.DataFrame()
    
import pandas as pd

def parteras():
    """
    Obtiene el número total de parteras por municipio, 
    filtrando por unidades con CLUES que empiezan por 'HGSSA'.

    Returns:
        pd.DataFrame: Con columnas ['Nombre Municipio Loc', 'Parteras'].
                      Retorna DataFrame vacío si hay errores.
    """
    try:
        # Cargar el archivo Parquet
        parteras = pd.read_parquet('assets/docs/Reporte Auxiliares, Casas de Salud y Parteras.parquet')
        
        if parteras.empty:
            print("Advertencia: El archivo está vacío.")
            return pd.DataFrame() 
        # Filtrar por CLUES que empiezan con 'HGSSA'
        parteras_filtradas = parteras[parteras['CLUES'].astype(str).str.startswith('HGSSA')]
        # Seleccionar columnas relevantes
        cols = ['Nombre Municipio Loc', 'Parteras']
        parteras_filtradas = parteras_filtradas[cols].copy()  # Usar copy() para evitar SettingWithCopyWarning
        # Eliminar filas con valores NaN en 'Parteras'
        parteras_filtradas.dropna(subset=["Parteras"], inplace=True)
        # Agrupar por municipio sumando las parteras
        parteras_total = parteras_filtradas.groupby('Nombre Municipio Loc')['Parteras'].sum().reset_index()
        return parteras_total
    
    except FileNotFoundError:
        print("Error: El archivo no se encontró.")
        return pd.DataFrame()  # Retorno consistente
    
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return pd.DataFrame()
    


def total_unidades_salud():
    """
    Obtiene el número total de unidades de salud por municipio,
    filtrando por CLUES que comienzan con 'HGSSA'.

    Returns:
        pd.DataFrame: Con columnas ['Nombre Municipio Loc', 'Total Unidades'].
                      Retorna DataFrame vacío si hay errores.
    """
    try:
        # Cargar el archivo Parquet
        unidades = pd.read_parquet('assets/docs/Reporte Auxiliares, Casas de Salud y Parteras.parquet')

        # Comprobar si el DataFrame está vacío inmediatamente después de cargarlo
        if unidades.empty:
            print("Advertencia: El archivo está vacío.")
            return pd.DataFrame()

        # --- Inicio de las operaciones de procesamiento ---

        # Asegurarse de que la columna 'CLUES' exista y sea string antes de filtrar
        if 'CLUES' not in unidades.columns:
             print("Error: La columna 'CLUES' no se encontró en el archivo.")
             return pd.DataFrame()

        # Asegurarse de que la columna 'Nombre Municipio Loc' exista
        if 'Nombre Municipio Loc' not in unidades.columns:
             print("Error: La columna 'Nombre Municipio Loc' no se encontró en el archivo.")
             return pd.DataFrame()


        # Filtrar, seleccionar columnas y eliminar duplicados en pasos lógicos.
        # Mantenemos el uso de .copy() para claridad y seguridad contra SettingWithCopyWarning.

        # 1. Filtrar por CLUES que comienzan con 'HGSSA'
        #    Usamos .astype(str) para manejar posibles valores no-string
        unidades_filtradas = unidades[unidades['CLUES'].astype(str).str.startswith('HGSSA')].copy()

        # Si después de filtrar no quedan unidades, podemos retornar un DataFrame vacío
        if unidades_filtradas.empty:
            print("Advertencia: No se encontraron unidades con CLUES que inicien con 'HGSSA'.")
            return pd.DataFrame()

        # 2. Seleccionar las columnas relevantes
        cols = ['Nombre Municipio Loc', 'CLUES']
        unidades_procesar = unidades_filtradas[cols].copy()

        # 3. Eliminar duplicados basados en 'CLUES'
        #    Usamos inplace=True para modificar el DataFrame directamente, ahorrando memoria temporal.
        unidades_procesar.drop_duplicates(subset=["CLUES"], inplace=True)
        unidades_procesar.to_csv('assets/docs/comprobacion.csv') # Para depuración, muestra las primeras filas después de eliminar duplicados
        # 4. Agrupar por municipio y contar las unidades únicas
        #    Contamos 'CLUES' después de haber eliminado duplicados, asegurando el conteo de unidades únicas.
        #    reset_index renombra la columna de conteo a 'Total Unidades' y convierte la Serie resultante en DataFrame.
        total_unidades = unidades_procesar.groupby('Nombre Municipio Loc')['CLUES'].count().reset_index(name='Total Unidades')

        # --- Fin de las operaciones de procesamiento ---

        # Devolver el DataFrame con el total por municipio
        total_unidades.to_csv('assets/docs/comprobacion_total_unidades.csv') # Para depuración, muestra las primeras filas después de eliminar duplicados
        return total_unidades

    except FileNotFoundError:
        # Manejo específico si el archivo no existe
        print("Error: El archivo no se encontró en la ruta especificada.")
        return pd.DataFrame() # Retorno consistente: DataFrame vacío

    except Exception as e:
        # Manejo de cualquier otro error inesperado
        # Hemos eliminado la línea duplicada aquí.
        print(f"Error inesperado durante el procesamiento de datos: {str(e)}")
        return pd.DataFrame() # Retorno consistente: DataFrame vacío