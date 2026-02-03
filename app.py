import streamlit as st
from src.utils.descriptions import SOLUTION_DESCRIPTION, SOLUTION_NAME
from src.utils.logger import MeuLogger

# Try to import modules that may require Selenium. If Selenium (or other
# runtime-only dependencies) are missing in the deployment environment,
# catch the error and show a friendly message in the UI instead of crashing.
try:
    from src.utils.extract_pbi import ExtratorPBI
    from src.utils.extract_pentaho import df_vidas_operadora
    selenium_available = True
    selenium_import_error = None
except Exception as e:
    ExtratorPBI = None
    df_vidas_operadora = None
    selenium_available = False
    selenium_import_error = e

logger = MeuLogger.setup_logger()

st.set_page_config(page_title=SOLUTION_NAME)

st.title(SOLUTION_NAME)
st.write(SOLUTION_DESCRIPTION)

if not selenium_available:
    st.warning(
        "O Selenium (ou outra dependência) não está disponível no ambiente de execução.\n"
        "Se você estiver usando o Streamlit Cloud/Deploy, adicione um arquivo `requirements.txt` "
        "na raiz do repositório contendo `selenium` e `webdriver-manager`, e redeploy."
    )
    with st.expander("Detalhes do erro de importação"):
        st.write(str(selenium_import_error))

col1, col2 = st.columns(2)
with col1:
    st.link_button(
        "Ver Dashboard Power BI - ANS",
        "https://app.powerbi.com/view?r=eyJrIjoiYmJjOTgwYjUtYWU2YS00MTgzLWFmYzMtNjA0MTJhNDdjYWEzIiwidCI6IjlkYmE0ODBjLTRmYTctNDJmNC1iYmEzLTBmYjEzNzVmYmU1ZiJ9",
        icon="📊",
    )
with col2:
    st.link_button(
        "Ver Sala de Situação - ANS",
        "https://www.ans.gov.br/pentaho/content/saiku-ui/index.html?biplugin5=true&userid=penanoprod&password=PRDAUpent001",
        icon="📈",
    )

menu_options = [
    "Extrair Data da Ultima Atualização PBI",
    "Extrair Dados PBI - IGR",
    "Extrair Dados Pentaho - Vidas Operadora",
]

option = st.selectbox("Selecione uma opção:", menu_options)

col1, col2 = st.columns(2)
with col1:
    if st.button("Executar"):
        if not selenium_available:
            st.error(
                "Execução bloqueada: dependências necessárias (Selenium) não estão instaladas. "
                "Adicione `requirements.txt` e redeploy ou execute localmente com `pip install -r requirements.txt`."
            )
        else:
            if option == menu_options[0]:
                res = ExtratorPBI(logger).data_atualizacao()
                st.write(res)
            elif option == menu_options[1]:
                res = ExtratorPBI(logger).dados_IGR()
                st.write(res)
            elif option == menu_options[2]:
                res = df_vidas_operadora(["368253"])
                st.write(res)

with col2:
    if st.button("Limpar Tela"):
        st.rerun()
