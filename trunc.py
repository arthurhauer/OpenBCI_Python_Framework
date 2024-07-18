import csv

def truncar_csv(arquivo_entrada, arquivo_saida, num_linhas):
    # Ler o arquivo CSV original
    with open(arquivo_entrada, 'r', newline='', encoding='utf-8') as csvfile:
        leitor_csv = csv.reader(csvfile)
        linhas = list(leitor_csv)[:num_linhas]  # Seleciona as primeiras 'num_linhas' linhas

    # Reescrever o arquivo CSV com as linhas selecionadas
    with open(arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
        escritor_csv = csv.writer(csvfile)
        escritor_csv.writerows(linhas)

# Exemplo de uso
arquivo_entrada1 = "G:\\Meu Drive\\PDI\\UTFPR\\TCC\\Dataset\\train\\train\\subj1_series1_events.csv"
arquivo_saida1 = "G:\\Meu Drive\\PDI\\UTFPR\\TCC\\train1000\\subj1_series1_events_1000.csv"
arquivo_entrada2 = "G:\\Meu Drive\\PDI\\UTFPR\\TCC\\Dataset\\train\\train\\subj1_series2_events.csv"
arquivo_saida2 = "G:\\Meu Drive\\PDI\\UTFPR\\TCC\\train1000\\subj1_series2_events_1000.csv"
num_linhas = 1000  # Número de linhas que você deseja manter

truncar_csv(arquivo_entrada1, arquivo_saida1, num_linhas)
truncar_csv(arquivo_entrada2, arquivo_saida2, num_linhas)