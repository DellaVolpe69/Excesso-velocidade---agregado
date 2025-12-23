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


# --- LINK DIRETO DA IMAGEM NO GITHUB ---
url_imagem = (
    "https://raw.githubusercontent.com/DellaVolpe69/Images/main/AppBackground02.png"
)
url_logo = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/DellaVolpeLogoBranco.png"
fox_image = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/Foxy4.png"

st.markdown(
    f"""
    <style>
    /* Remove fundo padrão dos elementos de cabeçalho que às vezes ‘brigam’ com o BG */
    header, [data-testid="stHeader"] {{
        background: transparent;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


modulos_dir = Path(__file__).parent / "Modulos"

# Se o diretório ainda não existir, faz o clone direto do GitHub
if not modulos_dir.exists():
    print("📥 Clonando repositório Modulos do GitHub...")
    subprocess.run(
        [
            "git",
            "clone",
            "https://github.com/DellaVolpe69/Modulos.git",
            str(modulos_dir),
        ],
        check=True,
    )

# Garante que o diretório está no caminho de importação
if str(modulos_dir) not in sys.path:
    sys.path.insert(0, str(modulos_dir))

# Agora importa o módulo normalmente
# from Modulos import AzureLogin
from Modulos import ConectionSupaBase

###################################
# from Modulos.Minio.examples.MinIO import read_file  # ajuste o caminho se necessário


# ---------------------------------------------------
# IMPORTA CONEXÃO SUPABASE
# ---------------------------------------------------
sys.path.append(
    PureWindowsPath(
        r"\\tableau\Central_de_Performance\BI\Cloud\Scripts\Modulos"
    ).as_posix()
)
import ConectionSupaBase

supabase = ConectionSupaBase.conexao()


# ---------------------------------------------------
# FUNÇÕES DE BANCO
# ---------------------------------------------------
def carregar_dados():
    data = supabase.table("EXCESSO VELOCIDADE - AGREGADO").select("*").execute()
    return pd.DataFrame(data.data)


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
    DATA_TREINAMENTO,
):
    supabase.table("EXCESSO VELOCIDADE - AGREGADO").insert(
        {
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
            "DATA_TREINAMENTO": (
                DATA_TREINAMENTO.isoformat() if DATA_TREINAMENTO else None
            ),
        }
    ).execute()

    st.success("✅ Registro adicionado com sucesso!")


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

    if result.data:
        return result.data[0]
    return None


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
    DATA_TREINAMENTO,
):
    supabase.table("EXCESSO VELOCIDADE - AGREGADO").update(
        {
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
            "DATA_TREINAMENTO": DATA_TREINAMENTO,
        }
    ).eq("AGREGADO", AGREGADO).execute()

    st.success("✏️ Registro atualizado com sucesso!")


def deletar_registro_por_placa(AGREGADO):
    supabase.table("EXCESSO VELOCIDADE - AGREGADO").delete().eq(
        "AGREGADO", AGREGADO
    ).execute()

    st.success("🗑️ Registro deletado com sucesso!")


# ---------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA
# ---------------------------------------------------
st.set_page_config(
    page_title="EXCESSO VELOCIDADE - AGREGADO",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------
# CSS
st.markdown(
    f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
                        url("{url_imagem}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Inputs padrão: text_input, number_input, date_input, etc */
        input, textarea {{
            border: 1px solid white !important;
            border-radius: 5px !important;
        }}
        
        /* Selectbox (parte fechada) */
        .stSelectbox div[data-baseweb="select"] > div {{
            border: 1px solid white !important;
            border-radius: 5px !important;
        }}
        
        /* Date input container */
        .stDateInput input {{
            border: 1px solid white !important;
            border-radius: 5px !important;
        }}

        .stButton > button {{
            background-color: #FF5D01 !important;
            color: white !important;
            border: 2px solid white !important;
            padding: 0.6em 1.2em;
            border-radius: 10px !important;
            font-size: 1rem;
            font-weight: 500;
            font-color: white !important;
            cursor: pointer;
            transition: 0.2s ease;
            text-decoration: none !important;   /* 👈 AQUI remove de vez */
            display: inline-block;
        }}
        .stButton > button:hover {{
            background-color: white !important;
            color: #FF5D01 !important;
            transform: scale(1.03);
            font-color: #FF5D01 !important;
            border: 2px solid #FF5D01 !important;
        }}

        /* RODAPÉ FIXO */
        .footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.6);
            color: white;
            text-align: center;
            font-size: 14px;
            padding: 8px 0;
            text-shadow: 1px 1px 2px black;
        }}
        .footer a {{
            color: #FF5D01;
            text-decoration: none;
            font-weight: bold;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        
    </style>
""",
    unsafe_allow_html=True,
)


def rodape():
    st.markdown(
        """
        <div class="footer">
            © 2025 <b>Della Volpe</b> | Desenvolvido por <a href="#">Raphael Chiavegati Oliveira</a>
        </div>
    """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------
# STATE DA NAVEGAÇÃO
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
    st.markdown("Adicione, edite ou pesquise seus documentos!")
    st.button("➕ Adicionar", on_click=go, args=("add",))
    st.button("✏️ Editar / Excluir ", on_click=go, args=("edit",))


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
            st.error("⚠️ Esse Frota já existe! Vá na aba EDITAR para alterá-la")

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
                DATA_TREINAMENTO,
            )
        st.success("✅ Registro adicionado com sucesso!")

rodape()

# ===================================================
# ====================== EDITAR =====================
# ===================================================
if st.session_state.page == "edit":
    st.subheader("🔍 Buscar licenciamento por Agregado")

    bp_busca = st.text_input("Digite o Nº do Agregado")

    colA, colB = st.columns(2)

    with colA:
        if st.button("📋 Exibir todos os cadastros"):
            st.session_state.show_table = True

    with colB:
        if st.button("❌ Ocultar lista"):
            st.session_state.show_table = False

    if st.session_state.get("show_table"):
        df = carregar_dados()
        if df.empty:
            st.info("Nenhum registro encontrado no banco.")
        else:
            st.dataframe(df, use_container_width=True)

    if st.button("Buscar"):
        registro = buscar_por_placa(bp_busca)
        st.session_state.registro_encontrado = registro

        if not registro:
            st.error("Agregado não encontrada.")

    if st.session_state.get("registro_encontrado"):
        r = st.session_state.registro_encontrado

        st.subheader("✏️ Editar informações")

        agregado_original = r["AGREGADO"]

        new_operacao = st.text_input("Operação", r["OPERACAO"])

        new_frota = st.text_input("AGREGADO", r["AGREGADO"])

        new_matricula = st.text_input("Matricula", r["MATRICULA"])

        new_nome_motorista = st.text_input("Nome Motorista", r["NOME_MOTORISTA"])

        new_mes = st.text_input("Mes", r["MES"])

        new_ocorrencia = st.text_input("Ocorrencia", r["OCORRENCIA"])

        new_ano_ocorrencia = st.text_input("Ano da Ocorrencia", r["ANO_DA_OCORRENCIA"])

        new_data_ocorrencia = st.date_input(
            "Data da Ocorrencia", value=pd.to_datetime(r["DATA_OCORRENCIA"])
        )
        new_velocidade = st.text_input("Velocidade", r["VELOCIDADE"])

        new_status = st.text_input("Status", r["STATUS"])

        new_data_tratativa = st.date_input(
            "Data da Tratativa", value=pd.to_datetime(r["DATA_TRATATIVA"])
        )

        new_documento = st.text_input("Documento", r["DOCUMENTO"])

        new_justificativa = st.text_input("Justificativa", r["JUSTIFICATIVA"])

        new_percentual = st.text_input("Percentual", r["PERCENTUAL"])

        new_fez_treinamento = st.text_input("Fez Treinamento", r["FEZ_TREINAMENTO"])

        new_data_treinamento = st.date_input(
            "Data do Treinamento", value=pd.to_datetime(r["DATA_TREINAMENTO"])
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Salvar alterações"):
                atualizar_registro_por_placa(
                    new_operacao,
                    agregado_original,  # AGREGADO usado no WHERE
                    new_matricula,
                    new_nome_motorista,
                    new_mes,
                    new_ocorrencia,
                    new_ano_ocorrencia,
                    new_data_ocorrencia.isoformat() if new_data_ocorrencia else None,
                    new_velocidade,
                    new_status,
                    new_data_tratativa.isoformat() if new_data_tratativa else None,
                    new_documento,
                    new_justificativa,
                    new_percentual,
                    new_fez_treinamento,
                    new_data_treinamento.isoformat() if new_data_treinamento else None,
                )

                st.success("Registro atualizado com sucesso!")
                st.session_state.registro_encontrado = None

        with col2:
            if st.button("Excluir registro"):
                deletar_registro_por_placa(agregado_original)
                st.success("Registro excluído com sucesso!")
                st.session_state.registro_encontrado = None

rodape()
