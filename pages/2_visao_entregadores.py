
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
def top_delivers(df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
          .groupby(['City', 'Delivery_person_ID'])
          .mean()
          .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
          .reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index()

    return df3

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

st.set_page_config(page_title='Visão Entregadores', layout='wide')

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
st.header('Marketplace - Visão Entregadores')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1: # Visão Gerencial
    with st.container(): # Container 1: Métricas gerais
        st.markdown('### Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1: # Maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Entregador mais velho', maior_idade)
            
        with col2: # Menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Entregador mais novo', menor_idade)
        
        with col3: # Melhor condição de veículos
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição de veículo', melhor_condicao) 
        
        with col4: # Pior condição de veículos
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição de veículo', pior_condicao)
    
    with st.container(): # Container 2: Avaliações
        st.markdown("""---""")
        st.markdown('### Avaliações')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Avaliação média por entregador')
            df_avg_ratings_per_deliver = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                             .groupby('Delivery_person_ID')
                                             .mean()
                                             .reset_index())
            st.dataframe(df_avg_ratings_per_deliver)
        
        # Nessa coluna tem dois dataframes diferentes
        with col2:
            st.markdown('#### Avaliação média por trânsito')
            
            df_avg_std_rating_by_traffic = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                               .groupby('Road_traffic_density')
                                               .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std'] # mudança de nome das colunas
            
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index() # reset do index
            
            st.dataframe(df_avg_std_rating_by_traffic)
            #====================================================================================================#
            st.markdown('#### Avaliação média por clima')
            
            df_avg_std_rating_by_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                               .groupby('Weatherconditions')
                                               .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std'] # mudança de nome das colunas
            
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index() # reset do index
            
            st.dataframe(df_avg_std_rating_by_weather)
        
    # Container 3: Velocidade de entrega
    with st.container():
        st.markdown("""---""")
        st.markdown('### Velocidade de entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Top entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('#### Top entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)