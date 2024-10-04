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

st.set_page_config(
            layout =  'wide',
            page_title = 'Consultora do neto',
        )

#file_path = Path(__file__).parent/"db"/"hashed_pw.pkl"

#with file_path.open("rb") as file:
#  hashed_passwords = pickle.load(file)

#credentials = {
#    "usernames": {
#        "admin": {
#            "name": "Admin",
#            "password": hashed_passwords[0]
#        }
#    }
#}

#authenticator = stauth.Authenticate(credentials= credentials, cookie_name="st_session", cookie_key="key123", cookie_expiry_days= 1)
#authenticator.login()

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

def dados_cliente():
    nome = st.text_input('Nome', placeholder = 'Insira seu nome aqui')
    st.divider()
    col1,col2,col3,col4 = st.columns(4)
    doc1 = col1.text_input('RG', placeholder='Ex: 00')
    doc2 = col2.text_input('1', placeholder='Ex: 000',label_visibility= 'hidden')
    doc3 = col3.text_input('2', placeholder='Ex: 000',label_visibility= 'hidden')
    doc4 = col4.text_input('3', placeholder='Ex: 0',label_visibility= 'hidden')
    doc0 = f'{doc1}.{doc2}.{doc3}-{doc4}'
    col1,col2,col3,col4 = st.columns(4)
    doc5 = col1.text_input('CPF', placeholder='Ex: 000')
    doc6 = col2.text_input('4', placeholder='Ex: 000',label_visibility= 'hidden')
    doc7 = col3.text_input('5', placeholder='Ex: 000',label_visibility= 'hidden')
    doc8 = col4.text_input('6', placeholder='Ex: 00',label_visibility= 'hidden')
    doc9 = f'{doc5}.{doc6}.{doc7}-{doc8}'
    col1,col2,col3,col4,col5 = st.columns(5)
    endereco = col1.text_input('Endereço', placeholder='Insira seu endereço aqui')
    cidade = col2.text_input('Cidade', placeholder= 'Ex: Ribeirão Preto')
    cep = col3.text_input('CEP', placeholder='Ex: 14940-000')
    ddd = col4.text_input('Telefone', placeholder='DDD')
    tel = col5.text_input('7', placeholder='12345-1234',label_visibility= 'hidden')
    telefone = f'({ddd}) {tel}'
    st.session_state['nome'] = nome
    st.session_state['RG'] = doc0
    st.session_state['CPF'] = doc9
    st.session_state['Endereço'] = endereco
    st.session_state['Cidade'] = cidade
    st.session_state['CEP'] = cep
    st.session_state['Telefone'] = telefone

tipo_despesa = ['Moradia', 'Despesas Básicas', 'Alimentação', 'Despesas com Saúde', 'Educação', 'Transporte', 'Outros']

if 'despesas' not in st.session_state:
	st.session_state['despesas'] = []

def increment_counter1(despesa):
	st.session_state['despesas'].append(despesa)
          
def despesas_mensais():
    col1,col2,col3,col4 = st.columns(4)
    tp_despesa = col1.selectbox('Tipo de despesa', tipo_despesa)
    desc = col2.text_input('Descrição', placeholder = 'Ex: Compra supermercado')
    valor = col3.number_input('Valor', placeholder = 'Valor em R$')
    despesa = {'Tipo de despesa': tp_despesa,
                        'Descrição': desc,
                        'Valor' : valor}
    add = col4.button('Adicionar')
    if add:
        increment_counter1(despesa)
    
    despesas = st.session_state['despesas']
    df_despesas = pd.DataFrame(despesas, columns=['Tipo de despesa', 'Descrição', 'Valor'])
    st.dataframe(despesas)
    

    st.session_state['total_valor'] = df_despesas['Valor'].sum()

if 'dividas' not in st.session_state:
	st.session_state['dividas'] = []

def increment_counter2(divida):
	st.session_state['dividas'].append(divida)

def organizacao_dividas():
    col1,col2,col3,col4,col5,col6,col7,col8 = st.columns(8)
    credor = col1.text_input('Credor', placeholder = 'Ex: Banco o Brasil')
    desc_div = col2.text_input('Descrição', placeholder = 'Ex: Emprétimo consgnado')
    total_prest = col3.number_input('Total de prestações', placeholder = 'Ex: 12')
    prest_pend = col4.number_input('Prestações pendentes', placeholder = 'Ex: 6')
    valor_prest = col5.number_input('Valor das prestações', placeholder = 'Valor em R$')
    valor_venc = col6.number_input('Valor em atraso', placeholder = 'Valor em R$')
    valor_pg = col7.number_input('Valor a pagar', placeholder = 'Valor em R$')
    total_pg = col8.number_input('Total a pagar', placeholder = 'Valor em R$')
    divida = {'Credor' : credor,
               'Descrição da dívida' : desc_div,
               'Total de prestações' : total_prest,
               'Prestações pendentes' : prest_pend,
               'Valor das prestações': valor_prest,
               'Valor em atraso' : valor_venc,
               'Valor a pagar' : valor_pg,
               'Total a pagar' : total_pg}
    add = col8.button('Nova entrada')
    if add:
        increment_counter2(divida)
    
    dividas = st.session_state['dividas']
    df_dividas = pd.DataFrame(dividas, columns= ['Credor','Descrição da dívida','Total de prestações','Prestações pendentes','Valor das prestações','Valor em atraso','Valor a pagar','Total a pagar'])
    st.dataframe(dividas)

    st.session_state['total_atraso'] = df_dividas['Valor em atraso'].sum()
    st.session_state['total_valor_pagar'] = df_dividas['Valor a pagar'].sum()
    st.session_state['total_pagar'] = df_dividas['Total a pagar'].sum()

def upload_bd():
    nome = st.session_state['nome']
    total_atraso = st.session_state['total_atraso']
    total_valor_pagar = st.session_state['total_valor_pagar']
    total_pagar = st.session_state['total_pagar']
    total_valor = st.session_state['total_valor']
    despesas = st.session_state['despesas']
    dividas = st.session_state['dividas']
    nome = st.session_state['nome']
    rg = st.session_state['RG']
    cpf = st.session_state['CPF']
    endereco = st.session_state['Endereço']
    cidade = st.session_state['Cidade']
    cep = st.session_state['CEP']
    telefone = st.session_state['Telefone']

    despesas_mensais = {'Cliente' : nome,
               'Despesas' : despesas,
               'Total despesas' : total_valor}
    
    organizacao_dividas = {'Cliente' : nome,
                           'Dividas' : dividas,
                           'Total em atraso' : total_atraso,
                           'Total Valor a pagar' : total_valor_pagar,
                           'Total a pagar' : total_pagar}
    
    cliente = {'Nome' : nome,
               'RG' : rg,
               'CPF':cpf,
               'Endereço':endereco,
               'Cidade' : cidade,
               'CEP': cep,
               'Telefone' : telefone}
    
    confirma = st.button('Confirmar')
    if confirma:
        entry = [cliente]
        entry2 = [despesas_mensais]
        entry3 = [organizacao_dividas]
        coll.insert_many(entry)
        coll2.insert_many(entry2)
        coll3.insert_many(entry3)
        st.header('Parábens, seu cadastro foi concluído com sucesso, em breve entraremos em contato. Certifique-se de enviar o pdf do relatório no nosso whatsapp.')

def pagina_principal():
    st.title('NOME LIMPO AGORA')
    st.divider()
    st.header('*Cadastro de novos clientes*')
    dados_cliente()
    tab1,tab2,tab3 = st.tabs(['Despesas Mensais', 'Organização de dívidas Pessoais', 'Relatório SCR do BACEN'])


    with tab1:
        st.header('**Despesas Mensais**')
        st.markdown('Aqui você irá inserir as suas maiores dispesas mensais separadas por categoria')
        despesas_mensais()

    with tab2:
        st.header('**Organização de dívidas pessoais**')
        st.markdown('Aqui você irá inserir as suas dívidas, credores e o valor')
        organizacao_dividas()

    with tab3:
        st.markdown('Para dar prosseguimento no atendimento é necessário seguir os passos abaixo e nos encaminhar um pdf contendo o relatório SCR conforme:')
        col1,col2,col3 = st.columns(3)
        col1.write('1. Acesse o site:')
        col1.link_button('Site BCB','https://registrato.bcb.gov.br/registrato/login/')
        col1.write('2. Entre com a conta GOV.BR, Digite o seu CPF e senha')
        col1.image('files/Tutorial 01.png')
        col1.image('files/Tutorial 02.png')
        col1.image('files/Tutorial 03.png')
        col2.write('3. Selecione Empréstimos e Financiamentos (SCR)')
        col2.image('files/Tutorial 04.png')
        col2.write('4. Aceite os termos')
        col2.image('files/Tutorial 05.png')
        col2.image('files/Tutorial 06.png')
        col3.write('5. Gere o relatório e nos envie o arquivo em PDF')
        col3.image('files/Tutorial 07.png')
        col3.image('files/Tutorial 08.png')
        col3.image('files/Tutorial 09.png')
        col3.header('Whats para envio do relatório (16)00000-0000')

    st.divider()
    upload_bd()  

def main():
    #if st.session_state["authentication_status"]:
    pagina_principal()
    #elif st.session_state["authentication_status"] == False:
    #    st.error("Username/password is incorrect.")

    #elif st.session_state["authentication_status"] == None:
    #    st.warning("Please insert username and password")

if __name__ == '__main__':
    main()