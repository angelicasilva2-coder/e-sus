import json

import streamlit as st

from app import BarramentoESUS, Paciente, RoteadorInteligenteSUS


st.set_page_config(page_title="Triagem e-SUS — demonstração", page_icon="🏥")
st.title("Triagem e-SUS")
st.caption("Protótipo demonstrativo de encaminhamento por gravidade.")
st.warning(
    "Demonstração somente com dados fictícios. Não use para decisões clínicas "
    "nem informe dados reais de pacientes."
)

if "sistema_esus" not in st.session_state:
  st.session_state.sistema_esus = BarramentoESUS()
if "contador_demo" not in st.session_state:
  st.session_state.contador_demo = 1
if "resultado_triagem" not in st.session_state:
  st.session_state.resultado_triagem = None

with st.form("formulario_triagem"):
  nome = st.text_input("Nome fictício", value="Paciente Exemplo")
  idade = st.number_input("Idade fictícia", min_value=0, max_value=120, value=30)
  sintomas = st.multiselect(
      "Sintomas fictícios",
      [
          "Dor de cabeça",
          "Febre",
          "Tosse",
          "Dor torácica",
          "Falta de ar",
          "Náusea",
      ],
  )
  gravidade = st.select_slider(
      "Nível de gravidade",
      options=[1, 2, 3, 4, 5],
      value=2,
      format_func=lambda nivel: {
          1: "1 — Atenção primária",
          2: "2 — Baixa",
          3: "3 — Urgência",
          4: "4 — Alta",
          5: "5 — Emergência crítica",
      }[nivel],
  )
  enviar = st.form_submit_button("Processar triagem")

if enviar:
  if not nome.strip():
    st.session_state.resultado_triagem = None
    st.error("Informe um nome fictício para a demonstração.")
  elif not sintomas:
    st.session_state.resultado_triagem = None
    st.error("Selecione ao menos um sintoma fictício.")
  else:
    identificador_demo = f"DEMO-{st.session_state.contador_demo:04d}"
    paciente = Paciente(
        cpf=identificador_demo,
        nome=nome.strip(),
        idade=int(idade),
        sintomas=sintomas,
        nivel_gravidade=gravidade,
    )
    roteador = RoteadorInteligenteSUS(st.session_state.sistema_esus)
    st.session_state.resultado_triagem = roteador.processar_e_direcionar(
        paciente
    )
    st.session_state.contador_demo += 1

resultado = st.session_state.resultado_triagem
if resultado:
  st.subheader("Resultado da simulação")
  if resultado["sincronizado_e_sus"]:
    st.success("Atendimento registrado na simulação.")
  else:
    st.error("Não foi possível registrar: a unidade de destino está lotada.")

  coluna_unidade, coluna_status = st.columns(2)
  coluna_unidade.metric("Unidade de destino", resultado["unidade_direcionada"])
  coluna_status.metric("Status", resultado["status"])
  st.write(f"**Justificativa:** {resultado['justificativa_roteamento']}")

  unidade = next(
      unidade
      for unidade in st.session_state.sistema_esus.rede_unidades.values()
      if unidade["nome"] == resultado["unidade_direcionada"]
  )
  st.caption(
      "Ocupação simulada da unidade: "
      f"{unidade['ocupacao_atual']}/{unidade['capacidade_maxima']}"
  )
  with st.expander("Ver payload FHIR fictício"):
    st.code(
        json.dumps(
            resultado["payload_enviado_rnds"],
            indent=2,
            ensure_ascii=False,
        ),
        language="json",
    )

st.caption(
    "Os registros existem apenas durante esta sessão e não são enviados a "
    "serviços oficiais."
)
