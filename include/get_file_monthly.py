import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, date
import boto3

def is_first_thursday(date_str):
    """
    Verifica se a data fornecida (YYYY-MM-DD) é a primeira quinta-feira do mês.
    """
    try:
        dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
        return dt.weekday() == 3 and 1 <= dt.day <= 7
    except Exception as e:
        print(f"Erro ao validar data: {e}")
        return False

def get_latest_vcv_clinvar_data():
    base_url = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/"
    target_file = "ClinVarVCVRelease_00-latest.xml.gz"
    bucket_name = "clinvar-monthly-342016537087-us-east-2-an"
    
    try:
        hoje = date.today()
        primeiro_dia = hoje.replace(day=1)
        month_reference = primeiro_dia.strftime("%Y-%m-%d")
        dia_atual = hoje.day

        if dia_atual > 7:
            print('Data fora da primeira semana do mês. Não buscar arquivo hoje')
            return
        else:
            print(f"Acessando {base_url}...")
            response = requests.get(base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            target_data = None

            for tr in soup.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) >= 3:
                    link_tag = tds[0].find('a', href=True)
                    if link_tag and target_file in link_tag['href']:
                        file_date_raw = tds[2].text.strip()
                        target_data = file_date_raw[:10]
                        break

            if not target_data:
                print("Arquivo não encontrado.")
                return

            if not is_first_thursday(target_data):
                print(f"A data {target_data} não é da primeira quinta-feira do mês. Abortando.")
                return

            new_filename = f"ClinVarVCVRelease_{month_reference}.xml.gz"
            download_url = base_url + target_file

            print(f"Iniciando download e streaming para: {new_filename}")

            s3 = boto3.client("s3", region_name="us-east-2")

            key = f"raw/{month_reference}/{new_filename}"

            response = requests.get(download_url, stream=True, timeout=(60, 600))
            response.raise_for_status()

            s3.upload_fileobj(response.raw, bucket_name, key)

            print(f"Sucesso! Arquivo salvo no S3 como: s3://{bucket_name}/{key}")

    except Exception as e:
        print(f"Erro no processo de busca do arquivo consolidado mais recente do ClinVar: {e}")

if __name__ == "__main__":
    get_latest_vcv_clinvar_data()