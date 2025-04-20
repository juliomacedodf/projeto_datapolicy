from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
from datetime import datetime, timezone
import pymongo

# Função para formatar telefone
def formatar_telefone(telefone):
    if not telefone:
        return ""
    numeros = re.sub(r'\D', '', telefone)
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    elif len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    return telefone

# Função para extrair eventos de uma página
def extrair_eventos_pagina(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        blocos_html = soup.find_all('div', class_='panels-bootstrap-region-panel panel-default-conte__do___principal')
        eventos_pagina = []

        for bloco_html in blocos_html:
            bloco = bloco_html.get_text(separator="\n").strip()
            linhas = [linha.strip() for linha in bloco.split('\n') if linha.strip()]
            if len(linhas) < 4:
                continue

            try:
                nome_evento = linhas[0]
                local = linhas[2] if len(linhas) > 2 else ""

                horas = re.findall(r'\d{2}:\d{2}', bloco)
                hora_inicio = horas[0] if len(horas) > 0 else "00:00"
                hora_fim = horas[1] if len(horas) > 1 else "00:00"

                data_evento = datetime.now(timezone.utc).astimezone().date()
                data_inicio = f"{data_evento}T{hora_inicio}:00-03:00"
                data_fim = f"{data_evento}T{hora_fim}:00-03:00"

                info_extra_div = bloco_html.find('div', class_='views-field views-field-field-resp-reserva text-muted')
                organizador = telefone = email = ""

                if info_extra_div:
                    texto_info = info_extra_div.get_text(separator=" ").strip()

                    email_match = re.search(r'[\w\.-]+@[\w\.-]+', texto_info)
                    email = email_match.group(0) if email_match else ""

                    telefone_match = re.search(r'(?:\(?\d{2}\)?[\s-]?\d{4,5}[\s-]?\d{4})', texto_info)
                    telefone_raw = telefone_match.group(0) if telefone_match else ""
                    telefone = formatar_telefone(telefone_raw)

                    organizador = texto_info
                    if email:
                        organizador = organizador.replace(email, "")
                    if telefone_raw:
                        organizador = organizador.replace(telefone_raw, "")

                    organizador = re.sub(r'[\r\n\t]+', ' ', organizador)
                    organizador = re.sub(r'\s{2,}', ' ', organizador)
                    organizador = organizador.strip(" .,")

                eventos_pagina.append({
                    "nome_evento": nome_evento,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "local": local,
                    "organizador": organizador,
                    "telefone": telefone,
                    "email": email
                })

            except Exception as e:
                print(f"Erro ao processar um evento: {e}")
                continue

        return eventos_pagina

    except Exception as e:
        print(f"Erro ao acessar a página {url}: {e}")
        return []

# Loop nas páginas da agenda
base_url = "https://www.alesc.sc.gov.br/agenda"
todos_eventos = []
page = 0

while True:
    url = base_url if page == 0 else f"{base_url}?page={page}"
    print(f"Processando página {page + 1}...")
    eventos = extrair_eventos_pagina(url)

    if not eventos:
        print("Nenhum evento encontrado - fim das páginas")
        break

    todos_eventos.extend(eventos)
    page += 1

# Criar DataFrame final
df = pd.DataFrame(todos_eventos)
print(f"Total de eventos encontrados: {len(df)}")
print(df.head(10))

# Conexão com o MongoDB no Docker
cliente = pymongo.MongoClient("mongodb://mongodb_agenda:27017/")
db = cliente["agenda_db"]
colecao = db["eventos"]

# Transformar em JSON e inserir
dados = df.to_dict(orient="records")
colecao.delete_many({})
colecao.insert_many(dados)
print("Dados inseridos com sucesso no MongoDB!")

