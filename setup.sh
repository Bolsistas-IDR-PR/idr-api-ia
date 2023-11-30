#!/bin/bash

# Definir a URL para o instalador do Miniconda
MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"

# Definir o nome do ambiente Conda a ser criado
ENV_NAME="meu_ambiente"

# Loop para iterar sobre os argumentos
while getopts "n:" opt; do
  case $opt in
    n) ENV_NAME="$OPTARG"
    ;;
    \?) echo "Opção inválida: -$OPTARG" >&2
    ;;
  esac
done

# Baixar o Miniconda
echo "Baixando Miniconda..."
wget $MINICONDA_URL -O miniconda.sh

# Instalar o Miniconda
echo "Instalando Miniconda..."
bash miniconda.sh -b -p $HOME/miniconda

# Adicionar o Miniconda ao PATH
export PATH="$HOME/miniconda/bin:$PATH"

# Inicializar o Conda
echo "Inicializando Conda..."
source $HOME/miniconda/bin/activate

# Atualizar Conda
conda update -y conda

# Criar o ambiente Conda a partir do arquivo environment.yml
if [ -f "environment.yml" ]; then
    echo "Criando ambiente Conda a partir de environment.yml..."
    conda env create -f environment.yml -n $ENV_NAME
else
    echo "Arquivo environment.yml não encontrado. Criando ambiente Conda básico."
    conda create -n $ENV_NAME python=3.8 -y
fi

# Ativar o ambiente
echo "Ativando o ambiente Conda..."
source activate $ENV_NAME

echo "Instalação e configuração concluídas."