# Projeto idr Paraná

Para rodar o projeto são necessarios alguns passos:

1. Instalar o [python]()
2. Instalar o [pip]()
4. Instalar o [setup]() obs de chmod +x setup.sh


### Instalação do sistema
Rodando o sistema com o comando:
    
    ```bash
    $ ./setup.sh -n nome_do_seu_ambiente
    $ conda activate nome_do_seu_ambiente
    ```
### Rodando o sistema
    
    ``` 
     uvicorn index:app --reload
    ```



