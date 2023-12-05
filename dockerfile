# Use a imagem oficial do Python 3.10.13
FROM python:3.10.13

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o resto do seu código de aplicação para o diretório de trabalho
COPY . .

# Informe ao Docker que a aplicação escuta na porta 8000
EXPOSE 8000

# Defina o comando para rodar a aplicação usando Uvicorn
CMD ["uvicorn", "src/index:app", "--host", "0.0.0.0", "--port", "8000"]