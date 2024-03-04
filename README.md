Produto Tecnológico desenvolvido durante projeto de Mestrado "Novo framework baseado em Python para processamento de biossinais" do Programa em Engenharia Elétrica e Informática Industrial (CPGEI) da UTFPR - Campus Curitiba, sob orientação dos professores Dr. José Jair Alves Mendes Júnior e Dr. Daniel Prado de Campos.

# Como Gerar Uma Nova Documentação

1.  Pelo terminal entre na pasta onde está localizado o projeto OpenBCI_Python_Framework
2.  Inicie um virtual enviroment de python. Se você não possuir o pacote venv do python 
    instalado globalmente no seu PC você pode rodar o seguinte comando:</br>
    <b>Linux:</b> </br>
    ```
    python3 -m venv venv
    ```
    <b>Windows:</b> </br>
    ```
    py -m venv env
    ```
3. Entre no ambiente virtual do python do projeto:</br>
    <b>Linux:</b> </br>
    ```
    source venv/bin/activate
    ```
    <b>Windows:</b> </br>
    ```
    .\venv\Scripts\activate
    ``` 
4. Instale as bibliotecas do projeto:</br>
    <b>Linux/Windows:</b> </br>
    ```
    pip install -r requirements.txt
    ```
5. Execute o seguinte comando no terminal:</br>
    ```
    sphinx-apidoc -o docs .
    ```
6. Entre no diretório docs:
    ```
    cd ./docs 
    ```
7. Crie o html :
    ```
    make html
    ```

O novo html será gerado. Agora basta abrir o arquivo "OpenBCI_Python_Framework-main/docs/_build/html/index.html" no seu navergador.