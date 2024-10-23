import streamlit as st
import pandas as pd
import pickle
import streamlit_authenticator as stauth
from pathlib import Path
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import urllib
import urllib.parse
from datetime import datetime
#import xlsxwriter
#import io
#import pyautogui

st.set_page_config(
            layout =  'wide',
            page_title = 'Nome Limpo Agora',
        )

file_path = Path(__file__).parent/"db"/"hashed_pw.pkl"

with file_path.open("rb") as file:
  hashed_passwords = pickle.load(file)

credentials = {
    "usernames": {
        "admin": {
            "email": 'admin@gmail.com',
            "name": "Admin",
            "password": hashed_passwords[0]
        }
    }
}

authenticator = stauth.Authenticate(credentials= credentials, cookie_name="st_session", cookie_key="key123", cookie_expiry_days= 1)
authenticator.login()

mongo_user = st.secrets['MONGO_USER']
mongo_pass = st.secrets["MONGO_PASS"]

username = urllib.parse.quote_plus(mongo_user)
password = urllib.parse.quote_plus(mongo_pass)
client = MongoClient("mongodb+srv://%s:%s@cluster0.gjkin5a.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" % (username, password), ssl = True)
st.cache_resource = client
db = client.consultora
coll = db.cadastro_clientes
coll2 = db.despesas_mensais
coll3 = db.organizacao_dividas
coll4 = db.historico_atendimento

def clientes():
    clientes = coll.find({})

    clientesdf = []
    for item in clientes:
        clientesdf.append(item)

    df = pd.DataFrame(clientesdf, columns= ['_id', 'Nome','RG','CPF', 'Endereço', 'Cidade', 'CEP', 'Telefone'])
    df.drop(columns='_id', inplace=True)
    st.session_state['clientes'] = df

def exibindo_cliente():
    df = st.session_state['clientes']
    total_desp_df = st.session_state['total_desp_df']
    total_div_df = st.session_state['total_div_df']
    nome = df['Nome'].value_counts().index
    cliente = st.selectbox('Cliente', nome)
    st.session_state['cliente_atendimento'] = cliente
    desp_teste = coll2.find({'Cliente': cliente})
    teste = []
    for item in desp_teste:
        teste.append(item)
    desp = teste[0]['Despesas']
    df_desp = pd.DataFrame(desp)
    st.session_state['df_desp'] = df_desp

    div_teste = coll3.find({'Cliente': cliente})
    teste2 = []
    for item in div_teste:
        teste2.append(item)
    div = teste2[0]['Dividas']
    df_dividas = pd.DataFrame(div)

    df_cliente = df[df['Nome'] == cliente]
    col1,col2,col3 = st.columns(3)
    rg = df_cliente['RG'].value_counts().index[0]
    col1.metric('RG', rg)
    cpf = df_cliente['CPF'].value_counts().index[0]
    col2.metric('CPF', cpf)
    tel = df_cliente['Telefone'].value_counts().index[0]
    col3.metric('Telefone', tel) 
    endereco = df_cliente['Endereço'].value_counts().index[0]
    col1.metric('Endereço', endereco)
    cidade = df_cliente['Cidade'].value_counts().index[0]
    col2.metric('Cidade', cidade)
    cep = df_cliente['CEP'].value_counts().index[0]
    col3.metric('CEP', cep)

    st.divider()
    select = st.selectbox('Selecione', ('Despesas mensais', 'Organização de dívidas pessoais'))
    if select == 'Despesas mensais':
        st.header('Despesas mensais')
        st.data_editor(df_desp)
        total_desp = total_desp_df[total_desp_df['Cliente'] == cliente]['Total despesas'].value_counts().index[0]
        st.metric('Total de despesas', f'R$ {total_desp:,.2f}')
        #salvar_imagem = st.button('Confirmar')
        #if salvar_imagem:
            #minha_imagem = pyautogui.screenshot()
            #minha_imagem.save(Path(__file__).parent/"files"/'despesa.jpg')
            #printsc = ('files/despesa.jpg')
            #st.image(printsc)

    if select == 'Organização de dívidas pessoais':
        st.header('Organização de Dívidas pessoais')
        st.data_editor(df_dividas)
        total_atraso = total_div_df[total_div_df['Cliente'] == cliente]['Total em atraso'].value_counts().index[0]
        total_pagar = total_div_df[total_div_df['Cliente'] == cliente]['Total Valor a pagar'].value_counts().index[0]
        total_pg = total_div_df[total_div_df['Cliente'] == cliente]['Total a pagar'].value_counts().index[0]
        col1,col2,col3 = st.columns(3)
        col1.metric('Total em atraso',f'R$ {total_atraso:,.2f}')
        col2.metric('Total Valor a pagar',f'R$ {total_pagar:,.2f}')
        col3.metric('Total a pagar',f'R$ {total_pg:,.2f}')
        #salvar_imagem = st.button('Confirmar')
        #if salvar_imagem:
            #minha_imagem = pyautogui.screenshot()
            #minha_imagem.save(Path(__file__).parent/"files"/'dividas.jpg')
            #printsc = ('files/dividas.jpg')
            #st.image(printsc)

    #data1 = df_desp
    #output = io.BytesIO()
    #writer = pd.ExcelWriter(output, engine="xlsxwriter")
    #data1.to_excel(writer, index=False, sheet_name="sheet1")
    #writer.close()
    #data_bytes = output.getvalue()
    #col1.download_button("Download Excel", data = data_bytes, file_name= f"Despesas_mensais_{cliente}.xlsx")

    #data1 = df_dividas
    #output = io.BytesIO()
    #writer = pd.ExcelWriter(output, engine="xlsxwriter")
    #data1.to_excel(writer, index=False, sheet_name="sheet1")
    #writer.close()
    #data_bytes = output.getvalue()
    #col2.download_button("Download Excel", data = data_bytes, file_name= f"organizacao_dividas_{cliente}.xlsx")

    st.divider()

def despesas():
    despesas = coll2.find({})

    despesasdf = []
    for item in despesas:
        despesasdf.append(item)
    
    total_desp_df = pd.DataFrame(despesasdf, columns= ['_id', 'Cliente','Total despesas'])
    total_desp_df.drop(columns='_id', inplace=True)
    st.session_state['total_desp_df'] = total_desp_df

def dividas():
    dividas = coll3.find({})

    dividasdf = []
    for item in dividas:
        dividasdf.append(item)

    total_div_df = pd.DataFrame(dividasdf, columns= ['_id', 'Cliente','Total em atraso','Total Valor a pagar','Total a pagar'])
    total_div_df.drop(columns='_id', inplace=True)
    st.session_state['total_div_df'] = total_div_df

def log_atendimento():
    cliente = st.session_state['cliente_atendimento']
    col1,col2 = st.columns(2)
    data = col1.date_input('Data do atendimento', format='DD.MM.YYYY')
    atendimento = col2.text_area('Descrição da ação')
    
    log = {'Cliente' : cliente,
           'Data' : str(data),
           'log' : atendimento
           }
    
    action = st.button('Salvar')
    if action:
        entry = [log]
        coll4.insert_many(entry)

    log_atendimento = coll4.find({'Cliente' : cliente})

    log_atendimentodf = []
    for item in log_atendimento:
            log_atendimentodf.append(item)

    container = st.container(border=True)
    with container:
        if log_atendimentodf == []:
            pass
        else:
            pd.DataFrame(log_atendimentodf)[['Data','log']]

def pagina_principal():
    st.title('Nome Limpo Agora')
    st.divider()
    st.header('*Painel de Atendimento*')
    btn = authenticator.logout()
    if btn:
        st.session_state["authentication_status"] == None
    
    clientes()
    despesas()
    dividas()
    exibindo_cliente()
    log_atendimento()

def main():
    if st.session_state["authentication_status"]:
        pagina_principal()
    elif st.session_state["authentication_status"] == False:
        st.error("Username/password is incorrect.")

    elif st.session_state["authentication_status"] == None:
        st.warning("Please insert username and password")

if __name__ == '__main__':
    main()
