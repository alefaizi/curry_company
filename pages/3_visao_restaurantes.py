
#==================================================
# Import das Bibliotecas
#==================================================

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

#==================================================
# Funções
#==================================================
def avg_std_time_on_traffic(df1):
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']]
             .groupby(['City', 'Road_traffic_density'])
             .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', 
                  color='std_time', color_continuous_scale='RdBu', 
                  color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City'). agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig

def avg_std_time_delivery(df1, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                - op: Tipo de operação que precisa ser calculada
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão do tempo
            Output:
                - df: Dataframe com 2 colunas e 1 linha
    """
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
             .groupby(['Festival'])
             .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux

def distance(df1, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 
                'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply(lambda x: 
                                                 haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                 (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        
        avg_distance = np.round(df1['distance'].mean(), 2)
        
        return avg_distance
    
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 
                'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply(lambda x: 
                                                 haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                 (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        
        avg_distance = df1.loc[:, ['City','distance']].groupby('City').mean().reset_index()
        
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        
        return fig

def clean_code(df1):
    """ 
        Esta função tem a responsabilidade de limpar o dataframe 
        Executei a minha limpeza que tem algumas coisas a mais do que a que o professor usou nas aulas
        
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
    """
    # 1. Excluir linhas com dados NaN
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    linhas_vazias = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]
    linhas_vazias = df1['City'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]
    linhas_vazias = df1['Festival'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]
    
    # 2. Converção do tipo de coluna de dados
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int).copy()
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int).copy()

    # 3. Remover os espaços a esquerda e a direita das strings
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    
    # 4. Formatação da coluna de datas
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 5. Limpeza da coluna 'Time_taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

#==================================================
# Import e limpeza do dataset
#==================================================

df = pd.read_csv('dataset/train.csv')
df1 = clean_code(df)

#==================================================
# Barra Lateral no Streamlit
#==================================================

st.set_page_config(page_title='Visão Restaurantes', layout='wide')

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#===================================================
# Layout no Streamlit
#===================================================
st.header('Marketplace - Visão Restaurantes')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container(): # Primeiro Container: métricas gerais
        st.markdown('### Overall Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Qtde. Entregadores', delivery_unique)
        
        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('Distância média entregas', avg_distance)
                             
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('AVG entrega c/ Festival', df_aux)
        
        with col4:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('STD entrega c/ Festival', df_aux)
        
        with col5:
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('AVG entrega s/ Festival', df_aux)
        
        with col6:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('STD entrega s/ Festival', df_aux)
            
    with st.container(): # Segundo Container com um gráfico e um dataframe  
        st.markdown("""___""")
        st.markdown('### Título da sessão')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Gráfico')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)
            
        with col2:
            st.markdown('#### DataFrame')
            
            df_aux = (df1.loc[:, ['City', 'Type_of_order', 'Time_taken(min)']]
                     .groupby(['City', 'Type_of_order'])
                     .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            st.dataframe(df_aux)
        
    with st.container(): # Terceiro Container com duas pizzas
        st.markdown("""___""")
        st.markdown('### Distribuição do Tempo')
        
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('#### Pizza 1')
            fig = distance(df1, fig=True)
            st.plotly_chart(fig)
  
        with col2:
            st.markdown('#### Pizza 2')
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)