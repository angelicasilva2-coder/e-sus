# Projeto e-SUS — demonstração em Streamlit

Protótipo local que demonstra o encaminhamento de pacientes por nível de
gravidade e capacidade das unidades. A integração e-SUS/RNDS é simulada; este
projeto não envia dados a serviços oficiais nem deve ser usado para decisões
clínicas reais.

## Executar a interface

Crie e ative um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
```

No Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

No macOS/Linux:

```bash
source .venv/bin/activate
```

Depois, em qualquer sistema:

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

O Streamlit abre a interface no navegador. Os registros ficam somente na sessão
atual e desaparecem ao encerrá-la.

## Publicar no Streamlit Community Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io/) e entre com sua
   conta GitHub.
2. Crie um app apontando para este repositório, para a branch `main` e para o
   arquivo `streamlit_app.py`.
3. Selecione **Deploy**. O Streamlit instalará as dependências de
   `requirements.txt`.

## Testes

```bash
python -m unittest discover -v
```

Use somente dados fictícios. Não informe dados pessoais nem informações reais
de saúde. Este protótipo não é uma ferramenta clínica nem uma integração oficial
com o e-SUS/RNDS.
