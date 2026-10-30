import unittest

from app import BarramentoESUS, Paciente, RoteadorInteligenteSUS


class RoteadorInteligenteSUSTests(unittest.TestCase):
  def criar_paciente(self, nivel_gravidade: int = 4) -> Paciente:
    return Paciente(
        cpf="000.000.000-00",
        nome="Paciente Exemplo",
        idade=52,
        sintomas=["Dor torácica"],
        nivel_gravidade=nivel_gravidade,
    )

  def test_unidade_lotada_nao_registra_atendimento(self):
    sistema = BarramentoESUS()
    hospital = sistema.rede_unidades["HOSP_01"]
    hospital["ocupacao_atual"] = hospital["capacidade_maxima"]

    resultado = RoteadorInteligenteSUS(sistema).processar_e_direcionar(
        self.criar_paciente()
    )

    self.assertEqual(resultado["status"], "FALHA")
    self.assertFalse(resultado["sincronizado_e_sus"])
    self.assertEqual(
        hospital["ocupacao_atual"], hospital["capacidade_maxima"]
    )
    self.assertEqual(sistema.registro_nacional, {})

  def test_unidade_com_vaga_registra_atendimento(self):
    sistema = BarramentoESUS()
    ocupacao_inicial = sistema.rede_unidades["HOSP_01"]["ocupacao_atual"]

    resultado = RoteadorInteligenteSUS(sistema).processar_e_direcionar(
        self.criar_paciente()
    )

    self.assertEqual(resultado["status"], "SUCESSO")
    self.assertTrue(resultado["sincronizado_e_sus"])
    self.assertEqual(
        sistema.rede_unidades["HOSP_01"]["ocupacao_atual"],
        ocupacao_inicial + 1,
    )

  def test_gravidade_fora_do_intervalo_e_rejeitada(self):
    with self.assertRaises(ValueError):
      self.criar_paciente(nivel_gravidade=6)

  def test_unidade_desconhecida_e_rejeitada(self):
    sistema = BarramentoESUS()

    with self.assertRaises(ValueError):
      sistema.registrar_atendimento("cpf", {}, "UNIDADE_INEXISTENTE")


if __name__ == "__main__":
  unittest.main()
