
FROM quay.io/astronomer/astro-runtime:13.5.1

# Instalar dependências do sistema (se necessário para compilar pacotes)
USER root
RUN apt-get update && apt-get install -y git && apt-get clean

# Voltar para o usuário astro para instalar pacotes Python
USER astro

COPY requirements.txt .
RUN pip install -r requirements.txt
