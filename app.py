import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, dash_table
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
        'Reservado': '#FFC107',
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
                                    {'label': '🟡 Solo Reservados', 'value': 'reservado'},
                                    {'label': '🔴 Solo Promesados', 'value': 'promesado'}
                                ],
                                value='todos',
                                placeholder="Seleccionar estados"
                            ),
                        ], width=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Exportar Dashboard:", className="fw-bold mb-2"),
                            dbc.ButtonGroup([
                                dbc.Button("📧 Generar HTML para Email", id="btn-export-html", color="success", size="sm"),
                                dbc.Button("📊 Exportar Datos CSV", id="btn-export-csv", color="info", size="sm"),
                                dbc.Button("📸 Capturar PNG", id="btn-export-png", color="warning", size="sm"),
                            ], className="d-grid")
                        ], width=12)
                    ], className="mt-3"),
                    html.Hr(),
                    html.Div(id="info-filtros", className="text-muted"),
                    html.Div(id="export-status", className="mt-2")
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

@app.callback(
    Output('export-status', 'children'),
    [Input('btn-export-html', 'n_clicks'),
     Input('btn-export-csv', 'n_clicks'),
     Input('btn-export-png', 'n_clicks')],
    [State('filtro-pisos', 'value'),
     State('filtro-vista', 'value'),
     State('filtro-estados', 'value'),
     State('filtro-tipologia', 'value')],
    prevent_initial_call=True
)
def exportar_dashboard(btn_html, btn_csv, btn_png, pisos, vista, estados, tipologia):
    import datetime
    from plotly.subplots import make_subplots
    import plotly.io as pio
    
    if df_global is None:
        return dbc.Alert("❌ No hay datos para exportar", color="danger")
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Aplicar los mismos filtros que en el dashboard
        df_filtrado = df_global.copy()
        
        if pisos and len(pisos) > 0:
            df_filtrado = df_filtrado[df_filtrado['PISO'].isin(pisos)]
        
        tipos_sin_lago = [1, 2, 3, 11, 12, 13]
        tipos_con_lago = [4, 5, 6, 7, 8, 9, 10]
        
        if vista == 'sin_lago':
            df_filtrado = df_filtrado[df_filtrado['TIPO'].isin(tipos_sin_lago)]
        elif vista == 'con_lago':
            df_filtrado = df_filtrado[df_filtrado['TIPO'].isin(tipos_con_lago)]
        
        if estados == 'disponible':
            df_filtrado = df_filtrado[df_filtrado['ESTADO'] == 'Disponible']
        elif estados == 'reservado':
            df_filtrado = df_filtrado[df_filtrado['ESTADO'] == 'Reservado']
        elif estados == 'promesado':
            df_filtrado = df_filtrado[df_filtrado['ESTADO'] == 'Promesado']
        
        if tipologia and len(tipologia) > 0 and 'TIPOLOGIA' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['TIPOLOGIA'].isin(tipologia)]
        
        if button_id == 'btn-export-html':
            # Crear gráfico completo para HTML
            fig = crear_grafico_3d(df_filtrado)
            
            # Calcular métricas para incluir en HTML
            total_precio = df_filtrado['PRECIO'].sum() if 'PRECIO' in df_filtrado.columns else 0
            total_m2 = df_filtrado['M2'].sum() if 'M2' in df_filtrado.columns else 0
            promedio_uf_m2 = df_filtrado['UF/M2'].mean() if 'UF/M2' in df_filtrado.columns and len(df_filtrado) > 0 else 0
            total_departamentos = len(df_filtrado)
            
            # Estados
            disponibles = len(df_filtrado[df_filtrado['ESTADO'] == 'Disponible'])
            reservados = len(df_filtrado[df_filtrado['ESTADO'] == 'Reservado'])
            promesados = len(df_filtrado[df_filtrado['ESTADO'] == 'Promesado'])
            
            # Crear HTML personalizado
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard Inmobiliario - Reporte {timestamp}</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
                    .header {{ text-align: center; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                    .metrics {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                    .metric-row {{ display: flex; justify-content: space-around; margin: 10px 0; }}
                    .metric {{ text-align: center; padding: 10px; }}
                    .metric-value {{ font-size: 24px; font-weight: bold; color: #007BFF; }}
                    .metric-label {{ font-size: 12px; color: #6c757d; }}
                    .estado-disponible {{ color: #28A745; }}
                    .estado-reservado {{ color: #FFC107; }}
                    .estado-promesado {{ color: #DC3545; }}
                    h1 {{ color: #2C3E50; margin: 0; }}
                    h2 {{ color: #2C3E50; text-align: center; }}
                    .timestamp {{ color: #6c757d; font-size: 14px; text-align: center; margin-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🏢 Dashboard Inmobiliario</h1>
                    <p>Reporte generado automáticamente</p>
                    <div class="timestamp">Generado el: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</div>
                </div>
                
                <div class="metrics">
                    <h2>📊 MÉTRICAS TOTALES</h2>
                    <div class="metric-row">
                        <div class="metric">
                            <div class="metric-value">{total_departamentos}</div>
                            <div class="metric-label">Total Departamentos</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${total_precio:,.0f}</div>
                            <div class="metric-label">Total Precio</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{total_m2:,.1f} m²</div>
                            <div class="metric-label">Total Superficie</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{promedio_uf_m2:.2f}</div>
                            <div class="metric-label">Promedio UF/m²</div>
                        </div>
                    </div>
                    
                    <h2>📈 DISTRIBUCIÓN POR ESTADO</h2>
                    <div class="metric-row">
                        <div class="metric">
                            <div class="metric-value estado-disponible">{disponibles}</div>
                            <div class="metric-label">🟢 Disponibles</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value estado-reservado">{reservados}</div>
                            <div class="metric-label">🟡 Reservados</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value estado-promesado">{promesados}</div>
                            <div class="metric-label">🔴 Promesados</div>
                        </div>
                    </div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>🏢 Visualización 3D del Edificio</h2>
                    {fig.to_html(include_plotlyjs=True, div_id="grafico-3d")}
                </div>
            </body>
            </html>
            """
            
            filename = f"dashboard_inmobiliario_{timestamp}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return dbc.Alert([
                html.Strong("✅ HTML Generado: "), 
                f"Archivo '{filename}' creado exitosamente. ",
                html.Br(),
                "📧 Puedes enviarlo por email como adjunto."
            ], color="success")
        
        elif button_id == 'btn-export-csv':
            # Exportar datos filtrados a CSV
            filename = f"datos_dashboard_{timestamp}.csv"
            df_filtrado.to_csv(filename, index=False, encoding='utf-8-sig')
            
            return dbc.Alert([
                html.Strong("✅ CSV Generado: "), 
                f"Archivo '{filename}' con {len(df_filtrado)} registros creado."
            ], color="success")
        
        elif button_id == 'btn-export-png':
            # Exportar gráfico como imagen PNG
            fig = crear_grafico_3d(df_filtrado)
            filename = f"grafico_3d_{timestamp}.png"
            
            # Configurar para exportar como imagen
            fig.update_layout(
                width=1200,
                height=800,
                title=f"Dashboard Inmobiliario - {datetime.datetime.now().strftime('%d/%m/%Y')}"
            )
            
            pio.write_image(fig, filename, format='png', engine='kaleido')
            
            return dbc.Alert([
                html.Strong("✅ PNG Generado: "), 
                f"Imagen '{filename}' creada. Ideal para incluir en presentaciones."
            ], color="success")
            
    except Exception as e:
        return dbc.Alert(f"❌ Error al exportar: {str(e)}", color="danger")
    
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
    
    # Filtrar por estados
    if estados_seleccionados == 'disponible':
        df_filtrado = df_filtrado[df_filtrado['ESTADO'] == 'Disponible']
    elif estados_seleccionados == 'reservado':
        df_filtrado = df_filtrado[df_filtrado['ESTADO'] == 'Reservado']
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
    
    # Calcular métricas por estado
    estados = ['Disponible', 'Reservado', 'Promesado']
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
        
        # RESERVADOS
        html.H6("🟡 RESERVADOS", className="mb-2", style={'color': '#FFC107', 'fontWeight': 'bold'}),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Reservado']['cantidad']}", className="mb-0", style={'color': '#FFC107'}),
                    html.Small("Cantidad", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"${metricas_por_estado['Reservado']['precio']:,.0f}", className="mb-0", style={'color': '#FFC107'}),
                    html.Small("Precio Total", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Reservado']['m2']:,.1f} m²", className="mb-0", style={'color': '#FFC107'}),
                    html.Small("Superficie", className="text-muted")
                ], className="text-center p-1")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.H6(f"{metricas_por_estado['Reservado']['uf_m2']:.2f}", className="mb-0", style={'color': '#FFC107'}),
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
    total_reservados = metricas_por_estado['Reservado']['cantidad']
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
        'reservado': '🟡 Solo Reservados',
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
            html.Span(f"🟡 {total_reservados} Reservados", className="me-3"),
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