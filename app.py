import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

def cargar_datos(archivo_excel):
    try:
        df = pd.read_excel(archivo_excel)
        print(f"Datos cargados: {len(df)} departamentos")
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

def crear_grafico_3d(df_filtrado):
    """Crear solo el gráfico 3D del edificio"""
    
    colores_estados = {
        'Disponible': '#28A745',
        'Moncurri': '#FFC107',     # Cambio de Reservado a Moncurri
        'Promesado': '#DC3545',
        'Stock Ausente': '#6C757D'
    }
    
    posiciones = {
        3: (0, 1), 2: (1, 1), 1: (2, 1), 13: (4, 1), 12: (5, 1), 11: (6, 1),  # Norte
        4: (0, 0), 5: (1, 0), 6: (2, 0), 7: (3, 0), 8: (4, 0), 9: (5, 0), 10: (6, 0)  # Sur
    }
    
    escalera_pos = (3, 1)
    
    fig = go.Figure()
    
    # Crear cubos para cada departamento
    for _, depto in df_filtrado.iterrows():
        tipo = int(depto['TIPO'])
        if tipo not in posiciones:
            continue
            
        x, y = posiciones[tipo]
        z = depto['PISO']
        
        color = colores_estados.get(depto['ESTADO'], '#CCCCCC')
        
        precio = depto.get('PRECIO', 0)
        superficie = depto.get('M2', 0)
        uf_m2 = depto.get('UF/M2', 0)
        
        hover_text = f"""<b style='color:#2C3E50; font-size:14px;'>🏢 Tipo {tipo} - Piso {z}</b><br>
        <span style='color:#28A745;'><b>Estado:</b></span> <b>{depto['ESTADO']}</b><br>
        <span style='color:#007BFF;'><b>Precio:</b></span> <b>${precio:,.0f}</b><br>
        <span style='color:#FF6B6B;'><b>Superficie:</b></span> <b>{superficie} m²</b><br>
        <span style='color:#9C27B0;'><b>UF/m²:</b></span> <b>{uf_m2:.2f}</b>"""
        
        # Cubo del departamento
        fig.add_trace(go.Mesh3d(
            x=[x, x+1, x+1, x, x, x+1, x+1, x],
            y=[y, y, y+1, y+1, y, y, y+1, y+1],
            z=[z, z, z, z, z+1, z+1, z+1, z+1],
            i=[7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 7],
            color=color,
            opacity=1.0,
            hovertemplate=hover_text + "<extra></extra>",
            showscale=False
        ))
        
        # Bordes del cubo
        edges_x = [x, x+1, x+1, x, x, x, x+1, x+1, x+1, x+1, x, x, x, x+1, x+1, x]
        edges_y = [y, y, y+1, y+1, y, y, y, y, y+1, y+1, y+1, y+1, y, y, y+1, y+1]
        edges_z = [z, z, z, z, z, z+1, z+1, z+1, z+1, z, z, z+1, z+1, z+1, z+1, z]
        
        fig.add_trace(go.Scatter3d(
            x=edges_x, y=edges_y, z=edges_z,
            mode='lines',
            line=dict(color='black', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Escaleras
    pisos_filtrados = df_filtrado['PISO'].unique()
    for piso in pisos_filtrados:
        x_esc, y_esc = escalera_pos
        
        fig.add_trace(go.Mesh3d(
            x=[x_esc, x_esc+1, x_esc+1, x_esc, x_esc, x_esc+1, x_esc+1, x_esc],
            y=[y_esc, y_esc, y_esc+1, y_esc+1, y_esc, y_esc, y_esc+1, y_esc+1],
            z=[piso, piso, piso, piso, piso+1, piso+1, piso+1, piso+1],
            i=[7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 7],
            color='#E9ECEF',
            opacity=1.0,
            hovertemplate=f"<b style='color:#2C3E50;'>🚶‍♂️ ESCALERAS</b><br>Piso {piso}<extra></extra>",
            showscale=False
        ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(showticklabels=False, title='', showgrid=False, range=[0, 8]),
            yaxis=dict(showticklabels=False, title='', showgrid=False, range=[0, 2]),
            zaxis=dict(showticklabels=False, title='', showgrid=False, 
                      range=[1, max(df_filtrado['PISO']) + 1] if len(df_filtrado) > 0 else [1, 11]),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
            aspectmode='manual',
            aspectratio=dict(x=3, y=1, z=2),
            bgcolor='#F8F9FA'
        ),
        showlegend=False,
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# Crear la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# IMPORTANTE: Para deploy
server = app.server

# Cargar datos globalmente
df_global = cargar_datos("Datos.xlsx")

# Layout de la aplicación
app.layout = dbc.Container([
    
    # Header principal
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🏢 Dashboard Inmobiliario Interactivo", 
                       className="display-4 text-center mb-2",
                       style={'color': '#2C3E50', 'fontWeight': 'bold'}),
                html.P("Análisis integral de UF/M² con filtros dinámicos", 
                      className="lead text-center text-muted")
            ], className="bg-white rounded shadow-sm p-4 mb-4")
        ], width=12)
    ]),
    
    # Panel de filtros y estadísticas
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("🔍 Filtros y Controles", className="mb-0", style={'color': '#2C3E50'})
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Seleccionar Pisos:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='filtro-pisos',
                                multi=True,
                                placeholder="Todos los pisos seleccionados por defecto",
                                className="mb-3"
                            ),
                        ], width=4),
                        dbc.Col([
                            html.Label("Seleccionar Vista:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='filtro-vista',
                                options=[
                                    {'label': '🏔️ Todos los tipos', 'value': 'todos'},
                                    {'label': '🏪 Solo Sin Lago', 'value': 'sin_lago'},
                                    {'label': '🌊 Solo Con Lago', 'value': 'con_lago'}
                                ],
                                value='todos',
                                placeholder="Seleccionar vista",
                                className="mb-3"
                            ),
                        ], width=4),
                        dbc.Col([
                            html.Label("Seleccionar Tipología:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='filtro-tipologia',
                                multi=True,
                                placeholder="Todas las tipologías",
                                className="mb-3"
                            ),
                        ], width=4)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Vista Rápida:", className="fw-bold mb-2"),
                            dbc.ButtonGroup([
                                dbc.Button("🏠 Todos", id="btn-todos", color="outline-primary", size="sm"),
                                dbc.Button("🏔️ Pisos Altos", id="btn-altos", color="outline-success", size="sm"),
                                dbc.Button("🏪 Pisos Bajos", id="btn-bajos", color="outline-info", size="sm"),
                            ], className="d-grid")
                        ], width=6),
                        dbc.Col([
                            html.Label("Estados:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='filtro-estados',
                                options=[
                                    {'label': '📊 Todos los estados', 'value': 'todos'},
                                    {'label': '🟢 Solo Disponibles', 'value': 'disponible'},
                                    {'label': '🟡 Solo Moncurri', 'value': 'moncurri'},  # Cambio aquí
                                    {'label': '🔴 Solo Promesados', 'value': 'promesado'}
                                ],
                                value='todos',
                                placeholder="Seleccionar estados"
                            ),
                        ], width=6)
                    ]),
                    html.Hr(),
                    html.Div(id="info-filtros", className="text-muted")
                ])
            ], className="shadow-sm")
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="metricas-resumen", className="text-center")
                ])
            ], className="shadow-sm")
        ], width=4)
    ], className="mb-4"),
    
    # Gráfico 3D principal
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("🏢 Visualización 3D del Edificio", className="mb-0", style={'color': '#2C3E50'})
                ]),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-3d",
                        type="circle",
                        children=[
                            dcc.Graph(
                                id='grafico-3d',
                                config={
                                    'displayModeBar': True,
                                    'displaylogo': False,
                                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                                }
                            )
                        ]
                    )
                ])
            ], className="shadow-sm")
        ], width=12)
    ], className="mb-4")
    
], fluid=True, style={'backgroundColor': '#F8F9FA', 'minHeight': '100vh', 'padding': '20px'})

# Callbacks

@app.callback(
    [Output('filtro-pisos', 'options'),
     Output('filtro-pisos', 'value'),
     Output('filtro-tipologia', 'options'),
     Output('filtro-tipologia', 'value')],
    [Input('filtro-pisos', 'id')]
)
def inicializar_filtros(_):
    if df_global is not None:
        # Opciones de pisos
        pisos_disponibles = sorted(df_global['PISO'].unique())
        opciones_pisos = [{'label': f'Piso {piso}', 'value': piso} for piso in pisos_disponibles]
        
        # Opciones de tipología
        if 'TIPOLOGIA' in df_global.columns:
            tipologias_disponibles = sorted(df_global['TIPOLOGIA'].dropna().unique())
            opciones_tipologia = [{'label': f'{tip}', 'value': tip} for tip in tipologias_disponibles]
        else:
            opciones_tipologia = []
        
        return opciones_pisos, pisos_disponibles, opciones_tipologia, []
    return [], [], [], []

@app.callback(
    Output('filtro-pisos', 'value', allow_duplicate=True),
    [Input('btn-todos', 'n_clicks'),
     Input('btn-altos', 'n_clicks'),
     Input('btn-bajos', 'n_clicks')],
    prevent_initial_call=True
)
def botones_vista_rapida(btn_todos, btn_altos, btn_bajos):
    if df_global is None:
        return []
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    pisos_disponibles = sorted(df_global['PISO'].unique())
    
    if button_id == 'btn-todos':
        return pisos_disponibles
    elif button_id == 'btn-altos':
        piso_medio = sum(pisos_disponibles) / len(pisos_disponibles)
        return [p for p in pisos_disponibles if p > piso_medio]
    elif button_id == 'btn-bajos':
        piso_medio = sum(pisos_disponibles) / len(pisos_disponibles)
        return [p for p in pisos_disponibles if p <= piso_medio]
    
    return dash.no_update

@app.callback(
    [Output('grafico-3d', 'figure'),
     Output('metricas-resumen', 'children'),
     Output('info-filtros', 'children')],
    [Input('filtro-pisos', 'value'),
     Input('filtro-vista', 'value'),
     Input('filtro-estados', 'value'),
     Input('filtro-tipologia', 'value')]
)
def actualizar_dashboard(pisos_seleccionados, vista_seleccionada, estados_seleccionados, tipologias_seleccionadas):
    if df_global is None:
        fig_vacia = go.Figure()
        fig_vacia.add_annotation(text="❌ No se pudieron cargar los datos", x=0.5, y=0.5)
        return fig_vacia, html.Div("Error en datos"), "Error"
    
    # Filtrar datos por pisos
    if pisos_seleccionados and len(pisos_seleccionados) > 0:
        df_filtrado = df_global[df_global['PISO'].isin(pisos_seleccionados)]
    else:
        df_filtrado = df_global.copy()
    
    # Filtrar por vista (Sin Lago / Con Lago)
    tipos_sin_lago = [1, 2, 3, 11, 12, 13]
    tipos_con_lago = [4, 5, 6, 7, 8, 9, 10]
    
    if vista_seleccionada == 'sin_lago':
        df_filtrado = df_filtrado[df_filtrado['TIPO'].isin(tipos_sin_lago)]
    elif vista_seleccionada == 'con_lago':
        df_filtrado = df_filtrado[df_filtrado['TIPO'].isin(tipos_con_lago)]
    
    # Filtrar por estados (cambio de 'reservado' a 'moncurri')
    if estados_seleccionados == 'disponible':
        df_filtrado = df_filtrado[df_filtrado['ESTADO'] == 'Disponible']
    elif estados_seleccionados == 'moncurri':  # Cambio aquí
        df_filtrado = df_filtrado[df_filtrado['ESTADO'] == 'Moncurri']
    elif estados_seleccionados == 'promesado':
        df_filtrado = df_filtrado[df_filtrado['ESTADO'] == 'Promesado']
    
    # Filtrar por tipología
    if tipologias_seleccionadas and len(tipologias_seleccionadas) > 0 and 'TIPOLOGIA' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TIPOLOGIA'].isin(tipologias_seleccionadas)]
    
    # Crear gráfico 3D
    fig_3d = crear_grafico_3d(df_filtrado)
    
    # Calcular métricas totales
    total_precio = df_filtrado['PRECIO'].sum() if 'PRECIO' in df_filtrado.columns else 0
    total_m2 = df_filtrado['M2'].sum() if 'M2' in df_filtrado.columns else 0
    promedio_uf_m2 = df_filtrado['UF/M2'].mean() if 'UF/M2' in df_filtrado.columns and len(df_filtrado) > 0 else 0
    total_departamentos = len(df_filtrado)
    
    # Calcular métricas por estado (cambio aquí también)
    estados = ['Disponible', 'Moncurri', 'Promesado']  # Cambio de 'Reservado' a 'Moncurri'
    metricas_por_estado = {}
    
    for estado in estados:
        df_estado = df_filtrado[df_filtrado['ESTADO'] == estado]
        metricas_por_estado[estado] = {
            'cantidad': len(df_estado),
            'precio': df_estado['PRECIO'].sum() if 'PRECIO' in df_estado.columns else 0,
            'm2': df_estado['M2'].sum() if 'M2' in df_estado.columns else 0,
            'uf_m2': df_estado['UF/M2'].mean() if 'UF/M2' in df_estado.columns and len(df_estado) > 0 else 0
        }
    
    # Crear componente de métricas
    metricas_componente = html.Div([
        # Métricas Totales
        html.H5("📊 MÉTRICAS TOTALES", className="text-center mb-3", style={'color': '#2C3E50', 'fontWeight': 'bold'}),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4(f"{total_departamentos}", className="mb-0", style={'color': '#6C757D', 'fontWeight': 'bold'}),
                    html.Small("Total Departamentos", className="text-muted")
                ], className="text-center p-2 border rounded")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H4(f"${total_precio:,.0f}", className="mb-0", style={'color': '#007BFF', 'fontWeight': 'bold'}),
                    html.Small("Total Precio", className="text-muted")
                ], className="text-center p-2 border rounded")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H4(f"{total_m2:,.1f} m²", className="mb-0", style={'color': '#FF6B6B', 'fontWeight': 'bold'}),
                    html.Small("Total Superficie", className="text-muted")
                ], className="text-center p-2 border rounded")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H4(f"{promedio_uf_m2:.2f}", className="mb-0", style={'color': '#9C27B0', 'fontWeight': 'bold'}),
                    html.Small("Promedio UF/m²", className="text-muted")
                ], className="text-center p-2 border rounded")
            ], width=3)
        ], className="mb-4"),
        
        # Separador
        html.Hr(),
        
        # Métricas por Estado
        html.H5("📈 MÉTRICAS POR ESTADO", className="text-center mb-3", style={'color': '#2C3E50', 'fontWeight': 'bold'}),
        
        # DISPONIBLES
        html.H6("🟢 DISPONIBLES", className="mb-2", style={'color': '#28A745', 'fontWeight': 'bold'}),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Disponible']['cantidad']}", className="mb-0", style={'color': '#28A745'}),
                    html.Small("Cantidad", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"${metricas_por_estado['Disponible']['precio']:,.0f}", className="mb-0", style={'color': '#28A745'}),
                    html.Small("Precio Total", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Disponible']['m2']:,.1f} m²", className="mb-0", style={'color': '#28A745'}),
                    html.Small("Superficie", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Disponible']['uf_m2']:.2f}", className="mb-0", style={'color': '#28A745'}),
                    html.Small("Prom. UF/m²", className="text-muted")
                ], className="text-center p-1")
            ], width=3)
        ], className="mb-2"),
        
        # MONCURRI (cambio aquí)
        html.H6("🟡 MONCURRI", className="mb-2", style={'color': '#FFC107', 'fontWeight': 'bold'}),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Moncurri']['cantidad']}", className="mb-0", style={'color': '#FFC107'}),
                    html.Small("Cantidad", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"${metricas_por_estado['Moncurri']['precio']:,.0f}", className="mb-0", style={'color': '#FFC107'}),
                    html.Small("Precio Total", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Moncurri']['m2']:,.1f} m²", className="mb-0", style={'color': '#FFC107'}),
                    html.Small("Superficie", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Moncurri']['uf_m2']:.2f}", className="mb-0", style={'color': '#FFC107'}),
                    html.Small("Prom. UF/m²", className="text-muted")
                ], className="text-center p-1")
            ], width=3)
        ], className="mb-2"),
        
        # PROMESADOS
        html.H6("🔴 PROMESADOS", className="mb-2", style={'color': '#DC3545', 'fontWeight': 'bold'}),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Promesado']['cantidad']}", className="mb-0", style={'color': '#DC3545'}),
                    html.Small("Cantidad", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"${metricas_por_estado['Promesado']['precio']:,.0f}", className="mb-0", style={'color': '#DC3545'}),
                    html.Small("Precio Total", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Promesado']['m2']:,.1f} m²", className="mb-0", style={'color': '#DC3545'}),
                    html.Small("Superficie", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Promesado']['uf_m2']:.2f}", className="mb-0", style={'color': '#DC3545'}),
                    html.Small("Prom. UF/m²", className="text-muted")
                ], className="text-center p-1")
            ], width=3)
        ])
    ])
    
    # Información de filtros mejorada
    total_disponibles = metricas_por_estado['Disponible']['cantidad']
    total_moncurri = metricas_por_estado['Moncurri']['cantidad']  # Cambio aquí
    total_promesados = metricas_por_estado['Promesado']['cantidad']
    
    # Crear texto descriptivo de filtros
    filtros_texto = []
    
    if pisos_seleccionados and len(pisos_seleccionados) > 0:
        pisos_texto = ", ".join([f"Piso {p}" for p in sorted(pisos_seleccionados)])
        filtros_texto.append(f"Pisos: {pisos_texto}")
    else:
        filtros_texto.append("Pisos: Todos")
    
    vista_texto = {
        'todos': 'Todas las vistas',
        'sin_lago': '🏪 Sin Lago únicamente',
        'con_lago': '🌊 Con Lago únicamente'
    }
    filtros_texto.append(f"Vista: {vista_texto.get(vista_seleccionada, 'Todas')}")
    
    estado_texto = {
        'todos': 'Todos los estados',
        'disponible': '🟢 Solo Disponibles',
        'moncurri': '🟡 Solo Moncurri',  # Cambio aquí
        'promesado': '🔴 Solo Promesados'
    }
    filtros_texto.append(f"Estados: {estado_texto.get(estados_seleccionados, 'Todos')}")
    
    if tipologias_seleccionadas and len(tipologias_seleccionadas) > 0:
        tip_texto = ", ".join(tipologias_seleccionadas)
        filtros_texto.append(f"Tipologías: {tip_texto}")
    
    info_text = html.Div([
        html.P([
            "📊 ", html.Strong("Filtros aplicados: "), " | ".join(filtros_texto)
        ], className="mb-1"),
        html.P([
            html.Strong(f"Total: {total_departamentos} departamentos | "),
            html.Span(f"🟢 {total_disponibles} Disponibles", className="me-3"),
            html.Span(f"🟡 {total_moncurri} Moncurri", className="me-3"),  # Cambio aquí
            html.Span(f"🔴 {total_promesados} Promesados")
        ], className="mb-0")
    ])
    
    return fig_3d, metricas_componente, info_text

if __name__ == '__main__':
    if df_global is not None:
        print("🚀 Iniciando Dashboard Inmobiliario Interactivo...")
        print(f"✅ Datos cargados: {len(df_global)} departamentos")
        print(f"📊 Pisos disponibles: {sorted(df_global['PISO'].unique())}")
        print("🌐 Abra su navegador en: http://127.0.0.1:8050")
        app.run(debug=True, host='127.0.0.1', port=8050)
    else:
        print("❌ Error: No se pudo cargar 'Datos.xlsx'")
        print("📋 Verifique que el archivo existe y tiene las columnas: TIPO, PISO, ESTADO, UF/M2")