from playwright.sync_api import sync_playwright
from docx import Document
import re
from tkinter import Tk, filedialog

Tk().withdraw()  # Esconde a janela principal

#abre o selecionador de arquivos
caminho = filedialog.askopenfilename(
    title="Selecione um plano de aula",
    filetypes=[("Arquivos Word", "*.docx")]
)

if caminho:
    doc = Document(caminho)
    print("Arquivo selecionado:", caminho)

conteudo = ""

#cobre todas as células do arquivo pegando o conteudo delas
for tabela in doc.tables:
    for linha in tabela.rows:
        dados = [" ".join(celula.text.split()) for celula in linha.cells]
        
        #permite selecionar apenas a 1º e a 3º coluna caso não esteja entre as palavras proibidas
        try:
            if "turma" in dados[0].lower():
                turma = dados[0].removeprefix("TURMA: ")
                print(dados[1].split()[1])
                dia = list(dados[1].split()[1]).pop(0) + list(dados[1].split()[1]).pop(1) + "/"
                data = dados[1].split()[1].replace("-","/")
                print(data)
                print(turma)
            elif dados[2].lower() not in ("inglês", "educação fisica", "educação digital", "componente curricular", "metodologia / estratégia"):
                conteudo += f"{dados[0]}\n"
                conteudo += f"{dados[2]}\n"
        except IndexError:
            pass

# variaveis
serie = {"4° ano.": "ENSINO FUNDAMENTAL I - 4º ANOQUARTO ANO", "5° ano." : "ENSINO FUNDAMENTAL I - 5º ANOQUINTO ANO" }
periodo = "Novas Matrículas - 2026"
bimestres = {"1": r"^1º BIMESTRE \(25\.0\)$", "2" :r"^2º BIMESTRE \(25\.0\)$", "3": r"^3º BIMESTRE \(25\.0\)$", "4": r"^4º BIMESTRE \(25\.0\)$", "r" :r"^RECUPERAÇÃO FINAL \(100\.0\)$"}
diciplina = r"^Todas as disciplinas do grupo$"
cpf = "----"
senha = "-----"

def login(pagina,cpf,senha):
    #prenche o nome de usuário
    pagina.locator('[id="formulario:login"]').fill(cpf)

    #prenche a senha
    pagina.locator('[id="formulario:senha"]').fill(senha)

    #avança pra pócima página
    pagina.click('[id="formulario:logar"]')


def selecao_perfil(pagina):
    # Abre a lista
    pagina.locator("#formulario_grupoAcessoLogin_chosen").click()

    # Espera o item ficar visível
    pagina.locator("li.active-result", has_text="PROFESSOR").wait_for()

    # Clica no item
    pagina.locator("li.active-result", has_text="PROFESSOR").click()

    #avança para proxima pagina
    pagina.locator('[id="formulario:selecionar"]').click()


def diario(pagina):
    pagina.get_by_role("link", name="Avaliação", exact=True).click()

    pagina.locator('[id="formMenu:j_id43:0:j_id52:5:j_id54"]').click()

    pagina.locator('[id="modalJustificativa:periodoLetivo"]').click()


def selecionar_periodo(pagina, periodo):
    pagina.select_option('[id="modalJustificativa\\:periodoLetivo"]',label=periodo)

    pagina.locator('[id="modalJustificativa:acessarDiario"]').click()

def selecao_turma(pagina, turma, diciplina, bimestre):
    #selecionara a turma
    pagina.get_by_text(turma).click()

    #selecionar a diciplina
    pagina.locator("div").filter(has_text=re.compile(diciplina)).nth(1).click()

    #selecionar o bimestre
    pagina.locator("div").filter(has_text=re.compile(bimestre)).nth(1).click()

def plano_de_aula(pagina, conteudo, data):
    pagina.get_by_role("columnheader", name=data).click()

    pagina.get_by_role("menuitem", name="Diário de Conteúdo").click()

    pagina.get_by_role("textbox", name="Conteúdo/matéria lecionada").fill(conteudo)

#inserir em qual bimestre esta
while True:
    try:
        bimestre_escolhido = bimestres[input("insira o número do bimestre atual")]
        break
    except KeyError:
        print("insira um valor válido")

#realiza a conexão com o site e insere as informações
with sync_playwright() as p:
    navegador = p.chromium.launch(headless=False,slow_mo=500)

    pagina = navegador.new_page()
    pagina.goto("https://sislamemg.caedufjf.net/sislamemg/login.faces")

    #login
    login(pagina,cpf,senha)

    #seleção de perfil
    selecao_perfil(pagina)

    #abrir diario
    diario(pagina)

    #selecionar período
    selecionar_periodo(pagina, periodo)

    #seleciona o dia e abre o diario
    selecao_turma(pagina, serie[turma], diciplina, bimestre_escolhido)

    #vai até a data atual
    pagina.get_by_role("button", name="Ir para data").click()
    pagina.get_by_role("textbox", name="Data").fill(data)
    pagina.get_by_role("button", name="Ir").click()
    
    #abre atualiza o plano de aula
    plano_de_aula(pagina, conteudo, dia)
    pagina.get_by_role("button", name="Salvar").click()

    input("pressione enter par fechar")
    navegador.close()

