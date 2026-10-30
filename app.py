import json
from datetime import datetime


class Paciente:

  def __init__(
      self,
      cpf: str,
      nome: str,
      idade: int,
      sintomas: list[str],
      nivel_gravidade: int,
  ):
    if not 1 <= nivel_gravidade <= 5:
      raise ValueError("O nível de gravidade deve estar entre 1 e 5.")

    self.cpf = cpf
    self.nome = nome
    self.idade = idade
    self.sintomas = sintomas
    self.nivel_gravidade = (
        nivel_gravidade  # 1 (Atenção Primária) a 5 (Emergência Crítica)
    )
    self.data_registro = datetime.now().isoformat()

  def para_padrao_fhir(self) -> dict:
    """Converte o objeto do banco local para a estrutura HL7 FHIR aceita pelo e-SUS/RNDS."""
    return {
        "resourceType": "Patient",
        "identifier": [
            {"system": "http://www.gov.br/fhir/r4/cpf", "value": self.cpf}
        ],
        "name": [{"text": self.nome}],
        "extension": [
            {
                "url": "http://esus.gov.br/fhir/StructureDefinition/sintomas",
                "valueString": ", ".join(self.sintomas),
            },
            {
                "url": "http://esus.gov.br/fhir/StructureDefinition/gravidade",
                "valueInteger": self.nivel_gravidade,
            },
        ],
    }


class BarramentoESUS:
  """Simula a API do e-SUS / RNDS (Rede Nacional de Dados em Saúde)."""

  def __init__(self):
    self.rede_unidades = {
        "UBS_01": {
            "nome": "UBS Central",
            "tipo": "Atenção Básica",
            "capacidade_maxima": 20,
            "ocupacao_atual": 8,
        },
        "UPA_01": {
            "nome": "UPA 24h Zona Sul",
            "tipo": "Urgência",
            "capacidade_maxima": 15,
            "ocupacao_atual": 12,
        },
        "HOSP_01": {
            "nome": "Hospital Geral de Alta Complexidade",
            "tipo": "Hospitalar",
            "capacidade_maxima": 10,
            "ocupacao_atual": 9,
        },
    }
    self.registro_nacional = {}

  def registrar_atendimento(self, cpf: str, fhir_payload: dict, unidade_id: str):
    if unidade_id not in self.rede_unidades:
        raise ValueError(f"Unidade desconhecida: {unidade_id}")

    unidade = self.rede_unidades[unidade_id]
    if unidade["ocupacao_atual"] >= unidade["capacidade_maxima"]:
        return False

    self.registro_nacional[cpf] = {
        "dados_paciente": fhir_payload,
        "unidade_alocada": unidade["nome"],
        "timestamp": datetime.now().isoformat(),
    }
    unidade["ocupacao_atual"] += 1
    return True


class RoteadorInteligenteSUS:
  """Camada de inteligência que analisa os dados da triagem e escolhe a unidade ideal."""

  def __init__(self, e_sus_api: BarramentoESUS):
    self.e_sus = e_sus_api

  def processar_e_direcionar(self, paciente: Paciente) -> dict:
    payload_fhir = paciente.para_padrao_fhir()

    # Algoritmo de Decisão/Roteamento Baseado em Risco e Capacidade da Rede
    if paciente.nivel_gravidade >= 4:
      unidade_id = "HOSP_01"
      justificativa = "Atendimento hospitalar de alta complexidade necessário."
    elif paciente.nivel_gravidade == 3:
      unidade_id = "UPA_01"
      justificativa = "Atendimento de urgência de médio porte (UPA)."
    else:
      unidade_id = "UBS_01"
      justificativa = (
          "Acompanhamento em Unidade Básica de Saúde (Atenção Primária)."
      )

    # Verifica lotação e ajusta roteamento se necessário
    unidade_alvo = self.e_sus.rede_unidades[unidade_id]
    if unidade_alvo["ocupacao_atual"] >= unidade_alvo["capacidade_maxima"]:
      return {
          "status": "FALHA",
          "paciente": paciente.nome,
          "cpf": paciente.cpf,
          "unidade_direcionada": unidade_alvo["nome"],
          "justificativa_roteamento": (
              justificativa + " Unidade lotada; atendimento não registrado."
          ),
          "sincronizado_e_sus": False,
          "payload_enviado_rnds": payload_fhir,
      }

    # Sincroniza com a base e-SUS
    sucesso_sync = self.e_sus.registrar_atendimento(
        paciente.cpf, payload_fhir, unidade_id
    )

    return {
        "status": "SUCESSO" if sucesso_sync else "FALHA",
        "paciente": paciente.nome,
        "cpf": paciente.cpf,
        "unidade_direcionada": unidade_alvo["nome"],
        "justificativa_roteamento": justificativa,
        "sincronizado_e_sus": sucesso_sync,
        "payload_enviado_rnds": payload_fhir,
    }


# ==============================================================================
# SIMULAÇÃO DE USO
# ==============================================================================
if __name__ == "__main__":
  # 1. Inicializa a rede e-SUS simulada e o software roteador
  sistema_central_esus = BarramentoESUS()
  roteador = RoteadorInteligenteSUS(sistema_central_esus)

  # 2. Simula o cadastro de um paciente na unidade hospitalar
  paciente_exemplo = Paciente(
      cpf="000.000.000-00",
      nome="Paciente Exemplo",
      idade=52,
      sintomas=["Dor torácica", "Falta de ar leve"],
      nivel_gravidade=4,  # Gravidade Alta
  )

  # 3. Processa a decisão e comunicação
  resultado = roteador.processar_e_direcionar(paciente_exemplo)

  print(json.dumps(resultado, indent=2, ensure_ascii=False))