import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitAppTests(unittest.TestCase):
  def setUp(self):
    app_path = Path(__file__).with_name("streamlit_app.py")
    self.app = AppTest.from_file(str(app_path)).run(timeout=30)

  def test_app_renders_without_exceptions(self):
    self.assertEqual(len(self.app.exception), 0)
    self.assertEqual(len(self.app.text_input), 1)

  def test_valid_form_shows_routing_result(self):
    self.app.text_input[0].set_value("Paciente Teste")
    self.app.multiselect[0].select("Febre")
    self.app.select_slider[0].set_value(4)
    self.app.button[0].click().run(timeout=30)

    self.assertEqual(len(self.app.exception), 0)
    self.assertEqual(len(self.app.success), 1)
    self.assertIn("Hospital", self.app.metric[0].value)

  def test_form_requires_at_least_one_symptom(self):
    self.app.text_input[0].set_value("Paciente Teste")
    self.app.button[0].click().run(timeout=30)

    self.assertEqual(len(self.app.exception), 0)
    self.assertIn(
        "Selecione ao menos um sintoma fictício.",
        [message.value for message in self.app.error],
    )


if __name__ == "__main__":
  unittest.main()
