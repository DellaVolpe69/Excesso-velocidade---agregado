import sys
import subprocess
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path, PureWindowsPath
import itertools
from requests_oauthlib import OAuth2Session
import time
import requests

# ---------------------------------------------------
# IMAGENS
# ---------------------------------------------------
url_imagem = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/AppBackground02.png"
url_logo = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/DellaVolpeLogoBranco.png"
fox_image = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/Foxy4.png"

st.markdown(
    """
    <style>
    header, [data-testid="stHeader"] {
        background: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# MODULOS
# ---------------------------------------------------
modulos_dir = Path(__file__).parent / "Modulos"

if not modulos_dir.exists():
    subprocess.run(
        ["git", "clone", "https://github.com/DellaVolpe69/Modulos.git", str(modulos_dir)],
        check=True
    )

if str(modulos_dir) not in sys.path:
    sys.path.insert(0, str(modulos_dir))

from Modulos import ConectionSupaBase

sys.path.append(
    PureWindowsPath(
        r'\\tableau\Central_de_Performance\BI\Cloud\Scripts\Modulos'
    ).as_posix()
)

supabase = ConectionSupaBase.conexao()

# ---------------------------------------------------
# FUNÇÕES BANCO
# ---------------------------------------------------
def carregar_dados():
    data = supabase.table("EXCESSO VELOCIDADE - AGREGADO").select("*").execute()
    return pd.DataFrame(data.data)


def FROTA_EXISTE(AGREGADO):
    result = (
        supabase.table("EXCESSO VELOCIDADE - AGREGADO")
        .select("AGREGADO")
        .eq("AGREGADO", AGREGADO)
        .execute()
    )
    return len(result.data) > 0


def buscar_por_placa(AGREGADO):
    result = (
        supabase.table("EXCESSO VELOCIDADE - AGREGADO")
        .select("*")
        .eq("AGREGADO", AGREGADO)
        .execute()
    )
    return result.data[0] if result.data else None


def adicionar_registro(
    OPERACAO,
    AGREGADO,
    MATRICULA,
    NOME_MOTORISTA,
    MES,
    OCORRENCIA,
    ANO_DA_OCORRENCIA,
    DATA_OCORRENCIA,
    VELOCIDADE,
    STATUS,
    DATA_TRATATIVA,
    DOCUMENTO,
    JUSTIFICATIVA,
    PERCENTUAL,
    FEZ_TREINAMENTO,
    DATA_TREINAMENTO
):
    supabase.table("EXCESSO VELOCIDADE - AGREGADO").insert({
        "OPERACAO": OPERACAO,
        "AGREGADO": AGREGADO,
        "MATRICULA": MATRICULA,
        "NOME_MOTORISTA": NOME_MOTORISTA,
        "MES": MES,
        "OCORRENCIA": OCORRENCIA,
        "ANO_DA_OCORRENCIA": ANO_DA_OCORRENCIA,
        "DATA_OCORRENCIA": DATA_OCORRENCIA.isoformat() if DATA_OCORRENCIA else None,
        "VELOCIDADE": VELOCIDADE,
        "STATUS": STATUS,
        "DATA_TRATATIVA": DATA_TRATATIVA.isoformat() if DATA_TRATATIVA else None,
        "DOCUMENTO": DOCUMENTO,
        "JUSTIFICATIVA": JUSTIFICATIVA,
        "PERCENTUAL": PERCENTUAL,
        "FEZ_TREINAMENTO": FEZ_TREINAMENTO,
        "DATA_TREINAMENTO": DATA_TREINAMENTO.isoformat() if DATA_TREINAMENTO else None
    }).execute()


def atualizar_registro_por_placa(
    OPERACAO,
    AGREGADO,
    MATRICULA,
    NOME_MOTORISTA,
    MES,
    OCORRENCIA,
    ANO_DA_OCORRENCIA,
    DATA_OCORRENCIA,
    VELOCIDADE,
    STATUS,
    DATA_TRATATIVA,
    DOCUMENTO,
    JUSTIFICATIVA,
    PERCENTUAL,
    FEZ_TREINAMENTO,
    DATA_TREINAMENTO
):
    (
        supabase.table("EXCESSO VELOCIDADE - AGREGADO")
        .update({
            "OPERACAO": OPERACAO,
            "AGREGADO": AGREGADO,
            "MATRICULA": MATRICULA,
            "NOME_MOTORISTA": NOME_MOTORISTA,
            "MES": MES,
            "OCORRENCIA": OCORRENCIA,
            "ANO_DA_OCORRENCIA": ANO_DA_OCORRENCIA,
            "DATA_OCORRENCIA": DATA_OCORRENCIA,
            "VELOCIDADE": VELOCIDADE,
            "STATUS": STATUS,
            "DATA_TRATATIVA": DATA_TRATATIVA,
            "DOCUMENTO": DOCUMENTO,
            "JUSTIFICATIVA": JUSTIFICATIVA,
            "PERCENTUAL": PERCENTUAL,
            "FEZ_TREINAMENTO": FEZ_TREINAMENTO,
            "DATA_TREINAMENTO": DATA_TREINAMENTO
        })
        .eq("AGREGADO", AGREGADO)
        .execute()
    )


def deletar_registro_por_placa(AGREGADO):
    (
        supabase.table("EXCESSO VELOCIDADE - AGREGADO")
        .delete()
        .eq("AGREGADO", AGREGADO)
        .execute()
    )

# ---------------------------------------------------
# CONFIG STREAMLIT
# ---------------------------------------------------
st.set_page_config(
    page_title="EXCESSO VELOCIDADE - AGREGADO",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# CSS
# ---------------------------------------------------
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
                url("{url_imagem}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

.stButton > button {{
    background-color: #FF5D01 !important;
    color: white !important;
    border-radius: 10px !important;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# RODAPÉ
# ---------------------------------------------------
def rodape():
    st.markdown("""
        <div class="footer">
            © 2025 <b>Della Volpe</b> | Desenvolvido por Raphael Chiavegati Oliveira
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# STATE
# ---------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "add"

if "show_table" not in st.session_state:
    st.session_state.show_table = False

def go(page):
    st.session_state.page = page

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:
    st.title("EXCESSO VELOCIDADE - AGREGADO")
    st.button("➕ Adicionar", on_click=go, args=("add",))
    st.button("✏️ Editar / Excluir", on_click=go, args=("edit",))

# ===================================================
# ===================== ADICIONAR ===================
# ===================================================
if st.session_state.page == "add":
    st.subheader("EXCESSO VELOCIDADE - AGREGADO")

    OPERACAO = st.text_input("OPERACAO")
    AGREGADO = st.text_input("AGREGADO")
    MATRICULA = st.text_input("MATRICULA")
    NOME_MOTORISTA = st.text_input("NOME_MOTORISTA")
    MES = st.text_input("MES")
    OCORRENCIA = st.text_input("OCORRENCIA")
    ANO_DA_OCORRENCIA = st.text_input("ANO_DA_OCORRENCIA")
    DATA_OCORRENCIA = st.date_input("DATA_OCORRENCIA")
    VELOCIDADE = st.text_input("VELOCIDADE KM/H")
    STATUS = st.text_input("STATUS")
    DATA_TRATATIVA = st.date_input("DATA_TRATATIVA")
    DOCUMENTO = st.text_input("DOCUMENTO")
    JUSTIFICATIVA = st.text_input("JUSTIFICATIVA")
    PERCENTUAL = st.text_input("PERCENTUAL")
    FEZ_TREINAMENTO = st.text_input("FEZ_TREINAMENTO")
    DATA_TREINAMENTO = st.date_input("DATA_TREINAMENTO")

    if st.button("Salvar"):
        if FROTA_EXISTE(AGREGADO):
            st.error("⚠️ Esse Frota já existe! Vá na aba EDITAR.")
        else:
            adicionar_registro(
                OPERACAO,
                AGREGADO,
                MATRICULA,
                NOME_MOTORISTA,
                MES,
                OCORRENCIA,
                ANO_DA_OCORRENCIA,
                DATA_OCORRENCIA,
                VELOCIDADE,
                STATUS,
                DATA_TRATATIVA,
                DOCUMENTO,
                JUSTIFICATIVA,
                PERCENTUAL,
                FEZ_TREINAMENTO,
                DATA_TREINAMENTO
            )
            st.success("✅ Registro adicionado com sucesso!")

    rodape()

# ===================================================
# ====================== EDITAR =====================
# ===================================================
if st.session_state.page == "edit":
    st.subheader("🔍 Buscar licenciamento por Agregado")

    bp_busca = st.text_input("Digite o Nº do Agregado")

    if st.button("Buscar"):
        st.session_state.registro_encontrado = buscar_por_placa(bp_busca)

    if st.session_state.get("registro_encontrado"):
        r = st.session_state.registro_encontrado
        agregado_original = r["AGREGADO"]

        new_operacao = st.text_input("Operação", r["OPERACAO"])
        new_matricula = st.text_input("Matricula", r["MATRICULA"])

        if st.button("Salvar alterações"):
            atualizar_registro_por_placa(
                new_operacao,
                agregado_original,
                new_matricula,
                r["NOME_MOTORISTA"],
                r["MES"],
                r["OCORRENCIA"],
                r["ANO_DA_OCORRENCIA"],
                r["DATA_OCORRENCIA"],
                r["VELOCIDADE"],
                r["STATUS"],
                r["DATA_TRATATIVA"],
                r["DOCUMENTO"],
                r["JUSTIFICATIVA"],
                r["PERCENTUAL"],
                r["FEZ_TREINAMENTO"],
                r["DATA_TREINAMENTO"]
            )
            st.success("✏️ Registro atualizado com sucesso!")

        if st.button("Excluir registro"):
            deletar_registro_por_placa(agregado_original)
            st.success("🗑️ Registro excluído com sucesso!")

    rodape()
