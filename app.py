import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import plotly.graph_objects as go
from funciones import obtener_datos, auxiliares_salud, casas_salud, parteras, total_unidades_salud

# Obtener datos
df_agrupado, municipios = obtener_datos()
total_auxiliares = None  # Inicializar variable para evitar errores si no se carga el DataFrame
if df_agrupado is None:
    raise ValueError("No se pudieron cargar los datos del archivo parquet.")
total_auxiliares = auxiliares_salud()


MAPEO_CASAS_SALUD = {
    'AE': {'code': 'AE', 'name': 'Adaptada Equipada', 'color': '#4e79a7'},
    'ASE': {'code': 'ASE', 'name': 'Adaptada sin Equipar', 'color': '#f28e2b'},
    'CE': {'code': 'CE', 'name': 'Construida Equipada', 'color': '#e15759'},
    'CSE': {'code': 'CSE', 'name': 'Construida sin Equipar', 'color': '#76b7b2'}
}
# Configuración de recursos externos
external_stylesheets = [
    dbc.themes.SLATE,
    dbc.icons.FONT_AWESOME,
    'https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Estilos personalizados
CUSTOM_STYLE = {
    "fontFamily": "'Open Sans', sans-serif",
    "fontWeight": 300
}

# Navbar
navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand(
            [
                html.I(className="fa fa-map-marked-alt me-2"),
                "Dashboard Municipal"
            ], 
            className="text-white fs-4",
            style={"fontWeight": 400} 
        ),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink(
                [html.I(className="fa fa-home me-1"), "Inicio"],
                href="#",
                className="text-white"
            )),
            dbc.NavItem(dbc.NavLink(
                [html.I(className="fa fa-chart-bar me-1"), "Estadísticas"],
                href="#",
                className="text-white"
            )),
        ], className="ms-auto")
    ]),
    color="#5B7389",
    dark=True,
    sticky="top",
    style={
        "boxShadow": "0 2px 10px rgba(0,0,0,0.3)",
        **CUSTOM_STYLE
    }
)

# Fila de filtros
filtros_row = dbc.Row(
    dbc.Col(
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Municipio", 
                                 className="text-white-50 mb-2",
                                 style={"fontWeight": 300}),
                        dcc.Dropdown(
                            id="dropdown-selector",
                            options=[{"label": mun, "value": mun} for mun in municipios],
                            value=municipios[0] if len(municipios) > 0 else None,
                            clearable=False,
                            searchable=True,
                            style={
                                "color": "#5B7389", 
                                "fontWeight": 300,
                                "backgroundColor": "#f8f9fa"
                            },
                        ),
                        html.Small(
                            "Selecciona un municipio para filtrar los datos",
                            className="text-muted d-block mt-1",
                            style={"fontWeight": 300}
                        )
                    ], md=6, className="pe-3"),
                    
                    dbc.Col([
                        html.Label("Opciones de visualización", 
                                 className="text-white-50 mb-2",
                                 style={"fontWeight": 300}),
                        dbc.Checklist(
                            options=[
                                {"label": " Mostrar gráficos", "value": 1},
                                {"label": " Mostrar datos brutos", "value": 2}
                            ],
                            value=[1],
                            id="switches-input",
                            switch=True,
                            labelStyle={
                                "fontWeight": 300,
                                "color": "white",
                                "marginRight": "15px"
                            },
                            inline=True
                        )
                    ], md=6)
                ])
            ]),
            className="bg-dark mb-4",
            style={
                "border": "1px solid #2c3e50",
                "boxShadow": "0 2px 10px rgba(0,0,0,0.2)"
            }
        ),
        width=12
    ),
    className="g-0",
    style={
        "padding": "1rem",
        "backgroundColor": "#1a1a1a",
        "borderBottom": "1px solid #2c3e50",
        "boxShadow": "0 2px 5px rgba(0,0,0,0.1)"
    }
)

# Contenido principal
content = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Información por Municipio",
                    className="text-center my-4 text-white",
                    style={
                        "textShadow": "1px 1px 3px rgba(0,0,0,0.3)",
                        "fontWeight": 300  
                    }
                ),
                width=12
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='piramide-poblacional',
                        config={'displayModeBar': False},
                        className="bg-dark rounded-3 p-2",
                        style={'height': '800px', 'overflow': 'hidden'}
                    ),
                    md=5,
                    className="pe-2"
                ),
                dbc.Col(
                    dcc.Graph(
                        id='grafico-secundario',
                        config={'displayModeBar': False},
                        className="bg-dark rounded-3 p-2",
                        style={'height': '800px', 'overflow': 'hidden'}
                    ),
                    md=4,
                    className="ps-2"
                ),
                dbc.Col(
                    html.Div(
                        [
                            # Card 1 - Población Total
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Población Total",
                                        className="text-white text-center",
                                        style={"backgroundColor": "#222831"}
                                    ),
                                    dbc.CardBody(
                                        html.Div([
                                            html.I(className="fas fa-users fa-2x text-white me-3"),  
                                            html.H1(id='poblacion-total', className="card-title text-white fw-bold mb-0")
                                        ], className="d-flex align-items-center justify-content-center")
                                    ),
                                    dbc.CardFooter(
                                        html.P("Habitantes", className="card-text text-center text-muted mt-1")
                                    )
                                ],
                                className="border-primary border-2 shadow-lg mb-3",
                                style={"minHeight": "180px"}
                            ),

                            dbc.Card(
                                [
                                    # 1. dbc.CardHeader: Solo el título, centrado y con el mismo estilo de fondo
                                    dbc.CardHeader(
                                        "Distribución por Sexo", # Texto del título
                                        className="text-white text-center", # Clases para texto blanco y centrado
                                        style={"backgroundColor": "#222831"} # Estilo para el color de fondo
                                    ),

                                    # 2. dbc.CardBody: Mantenemos la estructura de Row/Cols para la distribución,
                                    #    pero nos aseguramos de que los elementos internos tengan estilos consistentes.
                                    dbc.CardBody(
                                        # La estructura de Row y Col ya está diseñada para poner contenido uno al lado del otro.
                                        # No usaremos el Div flexbox del ejemplo anterior aquí, ya que no necesitamos
                                        # centrar un único ícono + valor, sino dos columnas de valores.
                                        dbc.Row([
                                            # Columna para Hombres
                                            dbc.Col([
                                                # El Div con el ID y el porcentaje. Mantendremos la clase display-6 para tamaño grande
                                                # y tus estilos de color específicos, ya que son parte de la visualización de la distribución.
                                                # Aseguramos texto centrado.
                                                html.Div(id='porcentaje-hombres', className="display-6 text-center", style={"color": "#AEC6CF"}),
                                                # La etiqueta para el valor, centrada y con estilo de texto atenuado/pequeño.
                                                html.Small("Hombres", className="text-muted d-block text-center")
                                            ]),
                                            # Columna para Mujeres
                                            dbc.Col([
                                                # Similar a la columna de hombres, manteniendo estilos y ID.
                                                html.Div(id='porcentaje-mujeres', className="display-6 text-center", style={"color": "#B8E2C8"}),
                                                html.Small("Mujeres", className="text-muted d-block text-center")
                                            ])
                                        ])
                                        # Aquí no incluiremos un ícono grande como en las otras tarjetas,
                                        # ya que la visualización principal es la distribución en dos columnas.
                                        # El ícono del header ya da contexto.
                                    ),

                                    # 3. dbc.CardFooter: Añadimos un pie de página consistente
                                    dbc.CardFooter(
                                        # Un párrafo para describir lo que muestran los números del cuerpo.
                                        # Clases similares al footer de las otras tarjetas.
                                        html.P(
                                            "Porcentaje", # Texto del footer
                                            className="card-text text-center text-muted mt-1" # Clases para texto centrado, atenuado y con margen superior
                                        )
                                    )
                                ],
                                # 4. dbc.Card principal: Aplicamos las mismas clases de borde, sombra, margen y estilo de altura mínima
                                className="border-primary border-2 shadow-lg mb-3", # Clases: borde primario, grosor 2, sombra grande, margen inferior
                                style={"minHeight": "180px"} # Estilo: altura mínima
),
                            
                            
                            # Card 3 - Grupo Mayoritario
                            dbc.Card(
                                    [
                                        # 1. dbc.CardHeader: Solo el título, centrado y con el mismo estilo de fondo
                                        dbc.CardHeader(
                                            "Grupo Mayoritario", # Texto del título
                                            className="text-white text-center", # Clases para texto blanco y centrado
                                            style={"backgroundColor": "#222831"} # Estilo para el color de fondo
                                        ),

                                        # 2. dbc.CardBody: Contenedor flexbox con el ícono y el valor (H1)
                                        dbc.CardBody(
                                            html.Div( # Usamos un Div con flexbox para alinear el ícono y el valor
                                                [
                                                    # El ícono se mueve aquí, con tamaño y margen similar al de la primera tarjeta
                                                    html.I(className="fas fa-child fa-2x text-white me-3"),
                                                    # El H1 con el ID, ahora centrado por el div flexbox
                                                    html.H1(
                                                        id='grupo-mayoritario', # Mantenemos el ID
                                                        # Clases similares a las del H1 de la primera tarjeta (texto blanco, negrita, sin margen inferior)
                                                        className="card-title text-white fw-bold mb-0"
                                                    )
                                                ],
                                                # Clases de flexbox para centrar vertical y horizontalmente
                                                className="d-flex align-items-center justify-content-center"
                                            )
                                            # El texto "Edad predominante" se moverá al footer
                                        ),

                                        # 3. dbc.CardFooter: Contiene el texto adicional
                                        dbc.CardFooter(
                                            # El párrafo con el texto adicional y clases de estilo similares al footer de la primera tarjeta
                                            html.P(
                                                "Edad predominante", # Texto
                                                className="card-text text-center text-muted mt-1" # Clases para texto centrado, atenuado y con margen superior
                                            )
                                        )
                                    ],
                                    # 4. dbc.Card principal: Aplicamos las mismas clases de borde, sombra, margen y estilo de altura mínima
                                    className="border-primary border-2 shadow-lg mb-3", # Clases: borde primario, grosor 2, sombra grande, margen inferior
                                    style={"minHeight": "180px"} # Estilo: altura mínima
                                ),
                                
                            # Card 4 - Densidad Poblacional
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        html.Div([
                                            html.I(className="fas fa-map-marked-alt me-2"),
                                            "Densidad Poblacional"
                                        ]),
                                        className="text-white",
                                        style={"backgroundColor": "#222831"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(id='densidad-poblacional', className="display-4 fw-bold text-white"),
                                                    html.Span("hab/km²", className="text-white-50 ms-2")
                                                ],
                                                className="mb-3 text-center"
                                            )
                                        ]
                                    )
                                ],
                                className="shadow",
                                style={"minHeight": "180px"}
                            )
                        ],
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "height": "100%",
                            "justifyContent": "space-between"
                        }
                    ),
                    md=3
                )
            ],
            className="mb-4"
        ),

        dbc.Row(
            html.Div(
            "Fuente: INEGI 2020 - https://www.inegi.org.mx/datosabiertos/",
            style={
                'textAlign': 'left',
                'fontStyle': 'italic',
                'fontSize': '12px',
                'color': '#666',
                'marginTop': '5px',
                'marginBottom': '30px',
            }
        )

        ),
        # Card de Auxiliares de Salud
        dbc.Row(
        [
        # Tarjeta Auxiliares de Salud (existente)
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.Div([
                            html.I(className="fas fa-user-md me-2"),
                            "Auxiliares de Salud"
                        ]),
                        className="text-white",
                        style={"backgroundColor": "#5B7389"}  
                    ),
                    dbc.CardBody(
                        [
                            html.Span(id='auxiliares-salud-card', className="display-4 fw-bold text-white"),
                            html.P("Número de auxiliares", className="card-text text-center text-white-50 small")
                        ],
                        className="d-flex flex-column align-items-center justify-content-center h-100"
                    )
                ],
                className="shadow h-100",
                style={"minHeight": "230px"}
            ),
            width=3  
        ),
        
        # Tarjeta Casas de Salud 
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.Div([
                                html.I(className="fas fa-house-medical me-2"),
                                "Casas de Salud"
                            ]),
                            className="text-white",
                            style={"backgroundColor": "#5B7389"}
                        ),
                        dbc.CardBody(
                            [
                                html.Div(
                                    id='casas-salud-card',
                                    style={
                                        'display': 'flex',
                                        'flexDirection': 'column',
                                        'height': '100%'
                                    }
                                ),
                            ],
                            style={
                                    'padding': '0.8rem',
                                    'flex': '1',
                                    'display': 'flex',
                                    'flexDirection': 'column'
                                }
                        )
                    ],
                    className="shadow h-100",
                    style={'height': '100%',
                            'minHeight': '230px'}
                ),
                width=3
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.Div([
                                html.I(className="fas fa-child me-2"),
                                "Parteras"
                            ]),
                            className="text-white",
                            style={"backgroundColor": "#5B7389"}
                        ),
                        dbc.CardBody(
                            [
                                html.H1(id='parteras-card', className="card-title text-center mb-1 text-white"),
                                html.P("Número de parteras", className="card-text text-center text-white-50 small")
                            ]
                        )
                    ],
                    className="shadow h-100",
                    style={'height': '100%',
                            'minHeight': '230px'}
                ),
                width=3
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.Div([
                                html.I(className="fas fa-child me-2"),
                                "Numero de unidades en el municipio"
                            ]),
                            className="text-white",
                            style={"backgroundColor": "#5B7389"}
                        ),
                        dbc.CardBody(
                            [
                                html.H1(id='total_unidades-card', className="card-title text-center mb-1 text-white"),
                                html.P("Unidades de salud", className="card-text text-center text-white-50 small")
                            ]
                        )
                    ],
                    className="shadow h-100",
                    style={'height': '100%',
                            'minHeight': '230px'}
                ),
                width=3
            )
        ],
        className="mb-4 g-3"  # g-3 añade separación horizontal entre columnas
    ),
            
    ],
    style={
        "padding": "1rem",
        "minHeight": "calc(100vh - 56px - 110px)",
        **CUSTOM_STYLE
    }
)
# Layout final
app.layout = html.Div(
    [
        navbar,
        filtros_row,
        content
    ],
    style={
        "backgroundColor": "#1a1a1a",
        **CUSTOM_STYLE
    }
)

# Callbacks para actualizar los gráficos y cards
@callback(
    [Output('piramide-poblacional', 'figure'),
     Output('grafico-secundario', 'figure'),
     Output('poblacion-total', 'children'),
     Output('porcentaje-hombres', 'children'),
     Output('porcentaje-mujeres', 'children'),
     Output('grupo-mayoritario', 'children'),
     Output('densidad-poblacional', 'children'),
     Output('auxiliares-salud-card', 'children'),  
     Output('casas-salud-card', 'children'),
     Output('parteras-card', 'children'),
     Output('total_unidades-card', 'children')],
    # Inputs del dropdown y switches  
    [Input('dropdown-selector', 'value'),
     Input('switches-input', 'value')]
)

def update_content(municipio_seleccionado, switches):
    # Datos del municipio seleccionado
    df_mun = df_agrupado.loc[municipio_seleccionado]
    
    # Crear pirámide poblacional
    fig_piramide = crear_piramide_poblacional(municipio_seleccionado)
    
    # Crear gráfico secundario
    fig_secundario = crear_grafico_secundario(municipio_seleccionado)
    
    # Calcular métricas para las cards
    total_poblacion = df_mun.sum().sum()
    columnas_hombres = [col for col in df_mun.index if col.endswith('_M')]
    columnas_mujeres = [col for col in df_mun.index if col.endswith('_F')]
    
    total_hombres = df_mun[columnas_hombres].sum().sum()
    total_mujeres = df_mun[columnas_mujeres].sum().sum()
    total_poblacion_sexo = total_hombres + total_mujeres  # Solo suma población por sexo
    
    # 2. Calcular porcentajes (asegurar que sumen 100%)
    porcentaje_hombres = f"{(total_hombres / total_poblacion_sexo * 100):.1f}%"
    porcentaje_mujeres = f"{(total_mujeres / total_poblacion_sexo * 100):.1f}%"
    
    # Verificación de redondeo (opcional)
    if abs(float(porcentaje_hombres[:-1]) + float(porcentaje_mujeres[:-1]) - 100) > 0.1:
        # Ajuste para que sumen exactamente 100%
        porcentaje_hombres = f"{(100 * total_hombres / total_poblacion_sexo):.1f}%"
        porcentaje_mujeres = "100.0%" if total_mujeres == 0 else f"{(100 - float(porcentaje_hombres[:-1])):.1f}%"
    # Formatear números con separadores de miles
    poblacion_total = f"{int(total_poblacion):,}"  # ✅ Asegura que sea entero antes del formato
   
    densidad = "128"  # Valor de ejemplo - deberías calcularlo según tus datos
    
    # Determinar grupo mayoritario (ejemplo simplificado)
    grupos_edad = [col[:-2] for col in df_mun.index if col.endswith('_M')]
    poblacion_por_grupo = {grupo: df_mun[f"{grupo}_M"] + df_mun[f"{grupo}_F"] for grupo in grupos_edad}
    grupo_mayoritario = max(poblacion_por_grupo.items(), key=lambda x: x[1])[0]
    grupo_mayoritario = grupo_mayoritario.replace("P_", "").replace("A", "-").replace("YMAS", "+")
    
    # auxiliares de salud 

    total_auxiliares = auxiliares_salud()
    auxiliares_municipio = total_auxiliares.loc[
    total_auxiliares['Nombre Municipio Loc'] == municipio_seleccionado,
        'Auxiliar de Salud'
        ].values[0] if not total_auxiliares.empty else 0

    auxiliares_formateados = f"{int(auxiliares_municipio):,}"  


  
    # CASAS DE SALUD
    # Procesamiento de Casas de Salud con detalle
    total_casas = casas_salud()
    casas_output = html.Div("Datos no disponibles")  # Valor por defecto

    if not total_casas.empty:
        casas_municipio = total_casas[total_casas['Nombre Municipio Loc'] == municipio_seleccionado]
        
        if not casas_municipio.empty:
            tipos_casas = casas_municipio.drop('Nombre Municipio Loc', axis=1)
            tipos_activos = tipos_casas.loc[:, (tipos_casas > 0).any()]
            
            if not tipos_activos.empty:
                total = tipos_activos.sum(axis=1).values[0]
                
                # --- VERSIÓN SIMPLIFICADA ---
                items_tipos = []
                for tipo, valor in tipos_activos.items():
                    # Traducir el código si existe en el mapeo, sino mostrar el código original
                    nombre = MAPEO_CASAS_SALUD.get(tipo, {}).get('name', tipo)
                    
                    item = html.Div([
                        html.Strong(f"{nombre}: "),  # Negrita para el tipo
                        html.Span(f"{valor.values[0]}")  # Valor normal
                    ], style={'marginBottom': '3px', 'fontSize': '0.9rem'})
                    
                    items_tipos.append(item)
                
                casas_output = html.Div([
                    html.H4(f"Total: {int(total):,}", style={'marginBottom': '10px'}),
                    html.Div(items_tipos)
                ])
            else:
                casas_output = "0"
        else:
            casas_output = "0"

    #parteras
    total_parteras = parteras()
    parteras_municipio = total_parteras.loc[
        total_parteras['Nombre Municipio Loc'] == municipio_seleccionado,
        'Parteras'
    ].values[0] if not total_parteras.empty else 0

    
    #Total de unidades
    unidades_filtradas = total_unidades_salud()
    total_unidades_municipio = unidades_filtradas.loc[
        unidades_filtradas['Nombre Municipio Loc'] == municipio_seleccionado,
        'Total Unidades'
    ].values[0] if not unidades_filtradas.empty else 0


    return (
        fig_piramide,
        fig_secundario,
        poblacion_total,
        porcentaje_hombres,
        porcentaje_mujeres,
        grupo_mayoritario,
        densidad,
        auxiliares_formateados,
        casas_output,
        parteras_municipio,
        total_unidades_municipio
    )

# Funciones para crear gráficos (igual que en tu versión original)
def crear_piramide_poblacional(municipio):
    df_mun = df_agrupado.loc[municipio]
    rangos_edad = [col[:-2] for col in df_mun.index if col.endswith('_M')]
    
    # Ordenar los rangos de edad de menor a mayor
    rangos_edad_ordenados = sorted(rangos_edad, key=lambda x: int(x.split('_')[1].split('A')[0]) if 'YMAS' not in x else 100)
    
    poblacion_f = df_mun[[f"{grupo}_F" for grupo in rangos_edad_ordenados]].astype(int).values.flatten()
    poblacion_m = df_mun[[f"{grupo}_M" for grupo in rangos_edad_ordenados]].astype(int).values.flatten() * -1
    
    # Diccionario para etiquetas más amigables
    etiquetas_edad = {
        "P_0A4": "0-4", "P_5A9": "5-9", "P_10A14": "10-14", "P_15A19": "15-19",
        "P_20A24": "20-24", "P_25A29": "25-29", "P_30A34": "30-34", "P_35A39": "35-39",
        "P_40A44": "40-44", "P_45A49": "45-49", "P_50A54": "50-54", "P_55A59": "55-59",
        "P_60A64": "60-64", "P_65A69": "65-69", "P_70A74": "70-74", "P_75A79": "75-79",
        "P_80A84": "80-84", "P_85YMAS": "85+"
    }
    
    grupos_edad_renombrados = [etiquetas_edad[grupo] for grupo in rangos_edad_ordenados]
    
  
    color_hombres = '#AEC6CF'  
    color_mujeres = '#B8E2C8'  
    
    fig = go.Figure()

    # Barras para hombres (lado izquierdo)
    fig.add_trace(go.Bar(
        y=grupos_edad_renombrados,
        x=poblacion_m,
        orientation='h',
        name='Hombres',
        marker=dict(
            color=color_hombres,
            line=dict(color='rgba(0,0,0,0.5)', width=0.5)
        ),
        hovertemplate='<b>Grupo de edad:</b> %{y}<br><b>Hombres:</b> %{customdata:,}<extra></extra>',
        customdata=abs(poblacion_m),
        text=[f'{abs(x):,}' for x in poblacion_m],
        textposition='outside',
        textfont=dict(color='white')
    ))

    # Barras para mujeres (lado derecho)
    fig.add_trace(go.Bar(
        y=grupos_edad_renombrados,
        x=poblacion_f,
        orientation='h',
        name='Mujeres',
        marker=dict(
            color=color_mujeres,
            line=dict(color='rgba(0,0,0,0.5)', width=0.5)
        ),
        hovertemplate='<b>Grupo de edad:</b> %{y}<br><b>Mujeres:</b> %{x:,}<extra></extra>',
        text=[f'{x:,}' for x in poblacion_f],
        textposition='outside',
        textfont=dict(color='white')
    ))

    # Calcular valores para los ejes
    max_val = max(max(abs(poblacion_m)), max(poblacion_f))
    tick_interval = max(1, int(max_val / 5))  # 5 marcas en el eje X

    # Actualizar diseño con la sintaxis correcta
    fig.update_layout(
        title={
            'text': f"Pirámide Poblacional - {municipio}",
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'white'}
        },
        xaxis=dict(
            title=dict(text="Población", font=dict(color='white')),
            tickfont=dict(color='white'),
            tickformat=",d",
            tickvals=list(range(-max_val, max_val+1, tick_interval)),
            ticktext=[str(abs(x)) for x in range(-max_val, max_val+1, tick_interval)],
            range=[-max_val*1.1, max_val*1.1],
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.3)'
        ),
        yaxis=dict(
            title=dict(text="Grupo de Edad", font=dict(color='white')),
            tickfont=dict(color='white'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        barmode="relative",
        bargap=0.1,
        bargroupgap=0.05,
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        hovermode="y unified",
        hoverlabel=dict(
            bgcolor='rgba(0,0,0,0.8)',
            font=dict(color='white')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color='white')
        ),
        margin=dict(l=100, r=100, t=80, b=80),
        height=700
    )

    return fig

# Función para crear el gráfico secundario (distribución por sexo)
def crear_grafico_secundario(municipio):
    df_mun = df_agrupado.loc[municipio]
    
    # Calcular totales por sexo
    total_mujeres = df_mun[[col for col in df_mun.index if col.endswith('_F')]].sum().sum()
    total_hombres = df_mun[[col for col in df_mun.index if col.endswith('_M')]].sum().sum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=['Mujeres', 'Hombres'],
        values=[total_mujeres, total_hombres],
        hole=0.4,
        marker=dict(colors=['#B8E2C8','#AEC6CF']),
        textinfo='percent+value',
        insidetextorientation='radial'
    ))
    

 
    fig.update_layout(
        #title=f"Distribución por Sexo - Municipio: {municipio}",
        title={
            'text': f"Distribución por Sexo - Municipio: {municipio}",
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'white'}
        },
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='white'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color='white')
        ),
        
    )
    
    return fig

if __name__ == "__main__":
    app.run(debug=True)