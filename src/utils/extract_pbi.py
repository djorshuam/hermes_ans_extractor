import json
import logging
import os
from pathlib import Path

import pandas as pd
import requests


class ExtratorPBI:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        project_root = os.getcwd()
        print(project_root)
        # Pasta que usamos como delimitador
        project_root = project_root.rsplit("src", 1)[0].rstrip(os.path.sep)

        print(project_root)
        # Carregar payload de Data
        payload_path_data = Path(project_root) / "payloads" / "payload_data.json"
        with open(payload_path_data, "r", encoding="utf-8") as f:
            self.payload_data = json.load(f)

        # Carregar payload de IGR (template)
        payload_path_igr = Path(project_root) / "payloads" / "payload_igr.json"
        with open(payload_path_igr, "r", encoding="utf-8") as f:
            self.payload_igr_template = f.read()  # Carregar como string para substituição

    def gerar_payload_igr(self, tipo_plano: str, mes: str, ano: str, porte: str) -> dict:
        """
        Gera payload IGR com parâmetros dinâmicos

        Args:
            tipo_plano: Segmentação do plano (ex: "Empresarial")
            mes: Nome do mês (ex: "Janeiro")
            ano: Ano (ex: 2024)
            porte: Porte da operadora (ex: "Grande Porte")

        Returns:
            dict: Payload pronto para requisição
        """
        # Substituir placeholders no template
        payload_str = self.payload_igr_template.replace("{{ANO}}", ano)
        payload_str = payload_str.replace("{{MES}}", mes)
        payload_str = payload_str.replace("{{PORTE}}", porte)
        payload_str = payload_str.replace("{{TIPO_PLANO}}", tipo_plano)

        # Converter string JSON para dicionário
        return json.loads(payload_str)

    # * Função para tratamento de dados e exportar dataframe
    def tratamento_dos_dados(self, data):
        """
        # Dados extração final
        * Extrai todos os dados possíveis da tabela
        * Processa e salva automaticamente
        """

        if data is not None:
            # Caminho até o array com os registros
            registros = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]

            linhas = []
            for item in registros:
                c = item["C"]  # lista de valores
                flag = item.get("R")  # pode não existir

                # Estrutura completa (6 valores) ou parcial (por causa de R)
                if flag is None:  # registro completo
                    linha = {
                        "Operadora": c[0],
                        "Média de reclamações": float(c[1]),
                        "Média de beneficiários": int(c[2]),
                        "IGR": round(float(c[3]), 2),
                        "Posição OPS mesmo porte": int(c[4]),
                        "Posição geral Setor": int(c[5]),
                    }
                    linhas.append(linha)
                # else:  # registro com dados faltantes
                #     linha = {
                #         "Operadora": c[0],
                #         "Média de reclamações": 1.0,
                #         "Média de beneficiários": int(c[1]),
                #         "IGR": round(float(c[2]), 2),
                #         "Posição OPS mesmo porte": int(c[3]),
                #         "Posição geral Setor": int(c[4]),
                #     }
                #     linhas.append(linha)

            df = pd.DataFrame(linhas)
            return df
        else:
            self.logger.error("\n❌ Falha na extração final")
            return None

    def extrair_dados(self, option: str):
        """
        Extrai dados de uma tabela do Power BI usando payloads predefinidos.
        * option: 'testado' para usar o payload testado e funcional.
        """
        if option == "Data":
            data = self.extrair(self.payload_data)
            if data is not None:
                # Caminho até o array com os registros
                registros = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"]
                self.logger.info(registros)
                return registros
            return None

        elif option == "sample_IGR":

            # Coluna de data
            data = self.extrair(self.payload_data)
            if data is not None:
                # Caminho até o array com os registros
                registros = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"]

            ano = "2025"
            mes = "jan"  # Apenas 1 mês
            tipo_plano = "Médico-hospitalar"  # Apenas 1 tipo
            porte = "Grande Porte"  # Apenas 1 porte

            dfs = []

            self.logger.info("🔄 Extraindo dados para o mês: %s/%s - %s - %s", mes, ano, porte, tipo_plano)
            payload = self.gerar_payload_igr(tipo_plano, mes, ano, porte)
            data = self.extrair(payload)
            df = self.tratamento_dos_dados(data)

            if df is not None and not df.empty:
                # * Adicionar colunas de contexto
                df["Mês"] = mes
                df["Ano"] = ano
                df["Tipo Plano"] = tipo_plano
                df["Porte"] = porte

                df["data_atualizacao"] = registros  # Adiciona a coluna de data

                record = df.iloc[0].to_dict()
                self.logger.info("Registro de amostra obtido")
                return record
            else:
                self.logger.warning("Nenhum registro encontrado para amostra")
                return None

        elif option == "IGR":

            # Coluna de data
            data = self.extrair(self.payload_data)
            if data is not None:
                # Caminho até o array com os registros
                registros = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"][0]["M0"]

            anos = ["2025"]
            lista_mes = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
            tipos = ["Médico-hospitalar", "Exclusivamente odontológica"]
            portes = ["Grande Porte", "Médio Porte", "Pequeno Porte"]

            dfs = []
            for ano in anos:
                for mes in lista_mes:
                    for porte in portes:
                        for tipo_plano in tipos:

                            self.logger.info(
                                "🔄 Extraindo dados para o mês: %s/%s - %s - %s", mes, ano, porte, tipo_plano
                            )
                            payload = self.gerar_payload_igr(tipo_plano, mes, ano, porte)
                            data = self.extrair(payload)
                            df = self.tratamento_dos_dados(data)

                            if df is not None and not df.empty:
                                # * Adicionar colunas de contexto
                                df["Mês"] = mes
                                df["Ano"] = ano
                                df["Tipo Plano"] = tipo_plano
                                df["Porte"] = porte
                                df["data_atualizacao"] = registros  # Adiciona a coluna de data
                                dfs.append(df)
                            else:
                                self.logger.warning("❌ Dados vazios para o mês: %s/%s", mes, ano)
            return pd.concat(dfs, ignore_index=True) if dfs else None

        # print("❌ Opção inválida. Use 'testado'.")
        return None

    def extrair(self, payload):
        """
        # Extrator usando payload que sabemos que funciona
        * Extrai todos os dados possíveis da tabela
        * Processa e salva automaticamente
        """

        # logger.info("🚀 Extração com payload...")

        url = "https://wabi-brazil-south-api.analysis.windows.net/public/reports/querydata?synchronous=true"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "ActivityId": "6577f9b3-cad2-9709-cf9f-f94a06ea196f",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "wabi-brazil-south-api.analysis.windows.net",
            "Origin": "https://app.powerbi.com",
            "Referer": "https://app.powerbi.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
            "X-PowerBI-ResourceKey": "bbc980b5-ae6a-4183-afc3-60412a47caa3",
        }

        try:
            # logger.info("⏱️  Fazendo requisição...")

            response = requests.post(url, headers=headers, json=payload, timeout=10)

            # print(f"📊 Status: {response.status_code}")

            if response.status_code == 200:

                self.logger.info("✅ Dados recebidos! Processando...")

                data = response.json()

                if "results" in data and data["results"]:
                    return data

            self.logger.error("❌ Erro ou sem dados")
            return None

        except (requests.RequestException, ValueError, KeyError) as e:
            self.logger.error("❌ Erro: %s", str(e))
            return None

    def data_atualizacao(self):
        """
        Extrai a data de atualização dos dados do Power BI.
        """
        return self.extrair_dados("Data")

    def dados_IGR(self):
        """
        Extrai a data de atualização dos dados do Power BI.
        """
        return self.extrair_dados("IGR")


# if __name__ == "__main__":
#     print("Iniciando extração de dados IGR...")
#     extrator = ExtratorPBI()

#     try:
#         data_igr = extrator.extrair_dados("Data")
#         logger.info("✅ Sucesso na extração dos dados IGR")
#     except (requests.RequestException, ValueError, KeyError, FileNotFoundError) as e:
#         logger.error("❌ Falha na extração dos dados IGR: %s", str(e))

# if __name__ == "__data_atualização__":
#     extrator = ExtratorPBI()
#     extrator.data_atualização()
