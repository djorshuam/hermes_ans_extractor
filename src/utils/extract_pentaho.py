import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from src.utils.logger import MeuLogger

# Configura logger
logger = MeuLogger.setup_logger()


def configurar_driver():
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")  # MODO INVISÍVEL
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def selecionar_cubo(driver, wait):
    cubo_dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select")))
    select = Select(cubo_dropdown)
    for option in select.options:
        if option.text.strip() and option.text.strip().lower() != "select a cube":
            select.select_by_visible_text(option.text)
            break
    time.sleep(3)
    return option.text


def adicionar_medidas(driver, wait):

    medidas_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.measure")))

    #medidas_links = driver.find_elements(By.CSS_SELECTOR, "a.measure")
    for medida_link in medidas_links:
        try:
            medida_link.click()
            time.sleep(0.5)
        except:
            continue


def clicar_categorias(driver):
    operadoras_section = driver.find_element(By.XPATH, "//*[contains(text(), 'Operadoras')]")
    operadoras_section.click()
    cobertura_section = driver.find_element(By.XPATH, "//*[contains(text(), 'Cobertura Assistencial')]")
    cobertura_section.click()
    residencia_section = driver.find_element(By.XPATH, "//*[contains(text(), 'Area Residência do Beneficiario')]")
    residencia_section.click()


def drag_multiple_safe(titles, driver):
    for title in titles:
        try:
            # Encontrar source com múltiplos xpaths
            source = None
            xpaths = [f"//li[contains(@class, 'ui-draggable')]//a[@title='{title}']", f"//a[@title='{title}']"]

            for xpath in xpaths:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            source = elem
                            break
                    if source:
                        break
                except:
                    continue

            if not source:
                logger.error(f"❌ Elemento '{title}' não encontrado")
                continue

            # Garantir visibilidade
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", source)
            time.sleep(0.3)

            # Target
            target = driver.find_element(By.CSS_SELECTOR, ".fields_list_body.rows.axis_fields")

            # Drag and drop
            ActionChains(driver).drag_and_drop(source, target).perform()
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Erro com '{title}': {e}")
            continue


def clicar_operadora(driver, wait, codigo_operadora):

    # Filtrar operadoras
    time.sleep(0.5)
    operadoras_section = driver.find_element(By.XPATH, "//*[contains(text(), 'Registro')]")
    operadoras_section.click()

    time.sleep(0.5)

    use_result_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Use Result')]")))
    use_result_label.click()

    use_result_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Use Result')]")))
    use_result_label.click()

    botao_remove = wait.until(EC.element_to_be_clickable((By.ID, "remove_all_members")))
    botao_remove.click()

    try:
        time.sleep(1)

        xpath = f"//input[@label='{codigo_operadora}']"
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        checkbox.click()

        botao_add = wait.until(EC.element_to_be_clickable((By.ID, "add_members")))
        botao_add.click()

        # CLICAR NO OK
        botao_ok = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#save']")))
        botao_ok.click()
        return True
    except:
        logger.error(f"❌ Operadora {codigo_operadora} não encontrada")
        # CLICAR NOK
        botao_nok = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#close']")))
        botao_nok.click()

    return False


def executar_consulta_e_obter_dados(driver, tempo):
    run_button = driver.find_element(By.ID, "run_icon")
    run_button.click()

    max_wait = tempo  # 10 minutos
    waited = 0
    while waited < max_wait:
        try:
            popup = driver.find_elements(By.XPATH, "//*[contains(text(), 'Running query')]")
            if not popup or not any(p.is_displayed() for p in popup):
                logger.info("✓ Processamento concluído!")
                break
        except:
            pass
        time.sleep(2)
        waited += 2

    # Aguardar mais um tempo extra para tabela aparecer
    time.sleep(1)

    # Procurar tabela
    table_found = False
    for attempt in range(10):  # 10 tentativas
        try:
            table_element = driver.find_element(By.XPATH, '//*[@id="table_14"]')
            if table_element.is_displayed():
                rows = table_element.find_elements(By.XPATH, ".//tr")
                if len(rows) > 1:
                    table_found = True
                    break
        except:
            pass
        time.sleep(2)

    if table_found:
        # Capturar dados
        table_html = table_element.get_attribute("outerHTML")
        df = pd.read_html(table_html, decimal=",", thousands=".")[0]
    else:
        logger.error("❌ Tabela não encontrada após todas as tentativas")

    df_preenchido = df.ffill()
    # Remover .0 e transformar em object
    df_preenchido["Registro"] = df_preenchido["Registro"].astype(str).str.replace(".0", "", regex=False)

    return df_preenchido


def df_vidas_operadora(operadoras: list[str]) -> pd.DataFrame:
    driver = configurar_driver()
    wait = WebDriverWait(driver, 10)

    try:
        url = "https://www.ans.gov.br/pentaho/content/saiku-ui/index.html?biplugin5=true&userid=penanoprod&password=PRDAUpent001"
        driver.get(url)

        cubo = selecionar_cubo(driver, wait)
        adicionar_medidas(driver, wait)

        clicar_categorias(driver)
        elementos = ["Registro", "Razao Social", "Cobertura Assistencial", "UF", "Nome  do municipio"]
        drag_multiple_safe(elementos, driver)

        df_final = pd.DataFrame()

        for operadora in operadoras:
            try:
                clicar_operadora(driver, wait, operadora)
                df1 = executar_consulta_e_obter_dados(driver, 600)

                logger.info(f"✅ Operadora {operadora} processada com sucesso!")

                if df_final.empty:  # Se usando DataFrame vazio
                    df_final = df1.copy()
                else:
                    df_final = pd.concat([df1, df_final], ignore_index=True)
            except:
                logger.warning(f"⚠️ Nenhum dado retornado para operadora {operadora}")
                continue

        # Remover duplicados no final
        df_final = df_final.drop_duplicates(ignore_index=True)

        df_final["Cubo"] = cubo
        return df_final

    finally:
        driver.quit()
