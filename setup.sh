#!/bin/bash

VENV_DIR=".myenv"

# Testa se o ambiente virtual já existe
if [ -d "$VENV_DIR" ]; then
    echo "O ambiente virtual já existe."
else
    # Cria o ambiente virtual
    echo "Criando ambiente virtual..."
    python3 -m venv $VENV_DIR
fi

# Testa se o ambiente virtual já está ativado
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "O ambiente virtual já está ativado."
else
    # Ativa o ambiente virtual
    echo "Ativando ambiente virtual..."
    source $VENV_DIR/Scripts/activate
fi

# Instala as dependências do projeto
echo "Instalando dependências..."
pip install -r req.txt

# Executa o aplicativo Flask
echo "Iniciando o aplicativo..."
export FLASK_APP=run.py
export FLASK_ENV=development

