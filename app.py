import pandas as pd
import json
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import boto3

pwd_ = {"aws_key": st.secrets["aws_key"],
"aws_secret_key" : st.secrets["aws_secret_key"]}

def GetJSON(key_ , aws_access_key_id, aws_secret_access_key):
        client = boto3.client('s3',aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
        f = client.get_object(Bucket = 'summer-song', Key= key_)
        text = f["Body"].read().decode()
        return json.loads(text)

def PutJSON(key_, list_ ,aws_access_key_id, aws_secret_access_key):
    client = boto3.client('s3',aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    response = client.put_object(
                Body=json.dumps(list_),
                Bucket='summer-song',
                Key=key_
    )
    return response

st.set_page_config(page_title="GOLDEN DECORADOS", 
                   page_icon="https://www.rivasciudad.es/wp-content/uploads/2023/08/Cortina-roja-de-teatro.png",
                   layout= "wide")

# Función para generar PDF
def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Títulos de columnas
    for col in df.columns:
        pdf.cell(100, 10, col, 1)
    pdf.ln()

    # Filas del DataFrame
    if len(df) <= 10:
        for i in range(len(df)):
            for col in df.columns:
                pdf.cell(100, 10, str(df.iloc[i][col])[0:30], 1)
            pdf.ln()
    else:
        for i in range(10):
            for col in df.columns:
                pdf.cell(100, 10, str(df.iloc[i][col])[0:30], 1)
            pdf.ln()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # Títulos de columnas
        for col in df.columns:
            pdf.cell(100, 10, col, 1)
        pdf.ln()
        for i in range(10,len(df)):
            for col in df.columns:
                pdf.cell(100, 10, str(df.iloc[i][col])[0:30], 1)
            pdf.ln()


    pdf_path = "/tmp/data.pdf"
    pdf.output(pdf_path)
    return pdf_path

try:
    if "passwords" not in st.session_state:
        with st.spinner("Loading App"):
            list_passwords = GetJSON("pwd_list.json", pwd_["aws_key"], pwd_["aws_secret_key"])
            st.session_state["passwords"] = list_passwords
            status_app = True
    else:
        list_passwords = st.session_state["passwords"]
        status_app = True
except:
    st.error("Unable to connect to DB")
    status_app = False

if status_app not in locals():
    status_app = True

if status_app:
    if "user" not in st.session_state or st.session_state["user"] == None:

        with st.form("Login"):
            user_ = st.text_input("Introduzca Usuario")
            password = st.text_input("Introduzca Contraseña")
            submitted = st.form_submit_button("Entrar")
            if submitted:
                count = st_autorefresh(interval=2000, limit=100, key="fizzbuzzcounter")

        if user_ != "" and password != "":
            continue_ = False

            for password_ in list_passwords:
                if password_["user"] == user_ and password_["password"] == password:
                    continue_ = True
                    st.session_state["user"] = user_
                    count = st_autorefresh(interval=100, limit=100, key="correct")
                    count2 = st_autorefresh(interval=100, limit=100, key="correct2")

            if continue_ == False:
                st.error("Usuario o contraseña erróneos")

    else:
        
        if "escenas" not in st.session_state:
            with st.spinner("Cargando Sesión"):
                dict_personajes = GetJSON("diccionario_personajes.json", pwd_["aws_key"], pwd_["aws_secret_key"])
                
                dict_escenas = GetJSON("diccionario_escenas.json", pwd_["aws_key"], pwd_["aws_secret_key"])
            
            st.session_state["escenas"] = dict_escenas
            st.session_state["personajes"] = dict_personajes
        else:
            dict_escenas = st.session_state["escenas"]
            dict_personajes = st.session_state["personajes"]



        if st.session_state["user"] == "golden":
            selected3 = option_menu("",[ "Reparto de Decorados","Documentos de interpretación",  "Asistencia", "Calendario", "Configuración"], 
                    icons=['kanban', 'person-badge', 'check-square',"calendar", "gear"], 
                    menu_icon="cast", default_index=0, orientation="horizontal",
                    styles={
                        "container": {"padding": "0!important", "background-color": "#00aa9b"},
                        "icon": {"color": "#ffffff", "font-size": "25px"}, 
                        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#f04641"},
                        "nav-link-selected": {"background-color": "#005573"},
                    }
                )
        
        else:
            selected3 = option_menu("",[ "Reparto de Decorados","Documentos de interpretación",  "Asistencia", "Calendario"], 
                    icons=['kanban', 'person-badge', 'check-square',"calendar"], 
                    menu_icon="cast", default_index=0, orientation="horizontal",
                    styles={
                        "container": {"padding": "0!important", "background-color": "#00aa9b"},
                        "icon": {"color": "#ffffff", "font-size": "25px"}, 
                        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#f04641"},
                        "nav-link-selected": {"background-color": "#005573"},
                    }
                )


        if selected3 == "Reparto de Decorados":
            

            if st.session_state["user"] == "golden":
                tab_personajes, tab_escenas = st.tabs(["Personajes", "Escenas"])

                with tab_personajes:
                    actor = st.selectbox(
                        "Elegir actor", options = list(dict_personajes.keys())
                    )
                    try:
                        st.dataframe(
                            pd.DataFrame(dict_personajes[actor]), use_container_width= True,hide_index=True
                        )
                    except:
                        pass
                with tab_escenas:
                    with st.expander("Ver todas las escenas"):
                        st.json(dict_escenas)
                    escena = st.selectbox("Elegir escena", list(dict_escenas.keys()))
                    list_escena_ = []
                    for mov_ in dict_escenas[escena]:
                        movimiento = list(mov_.keys())[0]
                        personas = " ,".join(mov_[movimiento])
                        list_escena_.append(
                            {
                                "MOVIMIENTO": movimiento,
                                "PERSONAS": personas
                            }
                        )
                    st.dataframe(list_escena_)
            else:
                all_ = st.toggle("Todas las escenas")

                if all_:
                    list_escenas_ = []
                    for escena_ in dict_personajes[st.session_state["user"].upper()]:
                        list_escenas_.append(escena_["ESCENA"])
                    data_ = pd.DataFrame(dict_personajes[st.session_state["user"].upper()])
                    list_dicts = []
                    for escena in dict_escenas:
                        if escena in list_escenas_:
                            data_filtered = data_[data_["ESCENA"] == escena]
                            for index, row in data_filtered.iterrows():
                                dict_ = {
                                    "ESCENA": row["ESCENA"],
                                    "MOVIMIENTO": row["MOVIMIENTO"]
                                }
                                list_dicts.append(dict_)
                        else:
                            dict_ = {
                                "ESCENA": escena,
                                "MOVIMIENTO": "--------"
                            }
                            list_dicts.append(dict_)
                    df = pd.DataFrame(list_dicts)

                else:
                    df = pd.DataFrame(dict_personajes[st.session_state["user"].upper()])

                st.dataframe(
                    pd.DataFrame(dict_personajes[st.session_state["user"].upper()]), use_container_width= True,hide_index=True
                )
                # Botón para descargar
                if st.button("Generar PDF"):
                    pdf_file = generar_pdf(df)
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="Descargar PDF",
                            data=f,
                            file_name=f"Movimientos_{st.session_state['user']}.pdf",
                            mime="application/pdf"
                        )
        
        elif selected3 == "Configuración":

            list_passwords = st.session_state["passwords"]
                
            data_passwords = pd.DataFrame(list_passwords)
            with st.expander("Usuarios"):
                st.table(data_passwords)
            tab_1, tab_2 = st.tabs(["Nuevo usuario", "Modificar usuario"])
            with tab_1:
                with st.form("Crear Usuario"):
                    user_ = st.text_input("Introduzca Usuario")
                    password = st.text_input("Introduzca Contraseña")
                    submitted = st.form_submit_button("Entrar")
                    if submitted:
                        if user_ != " " and password != " ":
                            count = st_autorefresh(interval=2000, limit=100, key="fizzbuzzcounter")
                            if user_ not in data_passwords["user"]:
                                list_passwords.append(
                                    {"user": user_, "password": password}
                                )
                                response = PutJSON(
                                    "pwd_list.json", list_passwords, 
                                    pwd_["aws_key"], pwd_["aws_secret_key"]
                                )
                                count = st_autorefresh(interval=2000, limit=100, key="writingfile")
                        else:
                            st.warning("Introduzca un usuario y contraseña correcta")
                        
                        count = st_autorefresh(interval=100, limit=100, key="newuser")
                        count = st_autorefresh(interval=100, limit=100, key="newuser2")
                
                if user_ in data_passwords["user"]:
                    st.warning("Ese usuario ya está registrado")
                
                if st.button("Reload"):
                    count = st_autorefresh(interval=100, limit=100, key="reload")

            with tab_2:
                with st.form("Actualizar Usuario"):
                    user_ = st.selectbox("Usuario", data_passwords[data_passwords["user"] != "golden"]["user"].tolist())
                    password = st.text_input("Introduzca Contraseña")
                    submitted = st.form_submit_button("Entrar")
                    if submitted:
                        if user_ != " " and password != " ":
                            count = st_autorefresh(interval=2000, limit=100, key="fizzbuzzcounter")
                            if user_ not in data_passwords["user"]:
                                list_passwords.append(
                                    {"user": user_, "password": password}
                                )
                                response = PutJSON(
                                    "pwd_list.json", list_passwords, 
                                    pwd_["aws_key"], pwd_["aws_secret_key"]
                                )
                                count = st_autorefresh(interval=2000, limit=100, key="rewritingfile")
                        else:
                            st.warning("Introduzca un usuario y contraseña correcta")
                        
                        count = st_autorefresh(interval=100, limit=100, key="newuser3")
                        count = st_autorefresh(interval=100, limit=100, key="newuser4")

                col_0_0, col_0_1 = st.columns(2)
                with col_0_0:  
                    if st.button("Reload "):
                        count = st_autorefresh(interval=100, limit=100, key="reload2")
                with col_0_1:
                    st.write(user_)
                    if st.button("Delete"):
                        final_list = []
                        for dict_ in list_passwords:
                            if dict_["user"] != user_:
                                final_list.append(dict_)
                        response = PutJSON(
                                    "pwd_list.json", final_list, 
                                    pwd_["aws_key"], pwd_["aws_secret_key"]
                                )
        else:
            st.write("Working on it")


        
        if st.button("Salir"):
            st.session_state["user"] = None
            count = st_autorefresh(interval=100, limit=100, key="salir")
            count2 = st_autorefresh(interval=100, limit=100, key="saliw")