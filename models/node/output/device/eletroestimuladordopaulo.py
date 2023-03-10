import csv
import os
from typing import List, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.output.output_node import OutputNode


class EletroEstimuladorDoPaulo(OutputNode):
    _MODULE_NAME: Final[str] = 'node.output.device.eletroestimuladordopaulo'

    INPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        raise NotImplementedError("Implementar a validação de parâmetros de entrada!")
        # Aqui você vai incluir condições para validar os parâmetros de configuração da sua classe, por exemplo: se porta de comunicação = -1, lançar erro!
        # Sugiro ver as outras classes implementadas para seguir o mesmo padrão de nomenclatura e afins Ex.:
        # models.node.generator.openbciboard
        # Já deixei alguns erros pré-importados ali em cima (linhas 5 e 6) para lançar as exceções corretas conforme o erro.

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        raise NotImplementedError("Implementar inicialização de parâmetros da classe!")
        # Aqui você vai inicializar todos as propriedades da classe (porta de comunicação, etc) e iniciar a comunicação com o dispositivo
        # Sugiro ver as outras classes implementadas para seguir o mesmo padrão de nomenclatura e afins Ex.:
        # models.node.generator.openbciboard

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN
        ]
        # Aqui você vai definir as entradas do seu nó. O padrão, se só houver 1, é 'main'.
        # A boa prática aqui, para manter o padrão, é definir o nome da entrada como um atributo estático da classe.

    def _run(self, data: FrameworkData, input_name: str) -> None:
        raise NotImplementedError("Implementar o tratamento dos dados!")
        # Aqui você vai ler os dados injetados no nó, e fazer o que for necessário. O coração da coisa! Ex.:
        # dados = data[self.INPUT_MAIN]
        # comando = 'desligar' if dados[length(dados)]<1 else 'ligar'
        # enviar_comando_para_dispositivo(comando)

    def dispose(self) -> None:
        super().dispose()
        # Aqui você vai definir o que deve acontecer quando a execução for finalizada. Ex.:
        # fechar comunicação com dispositivo, limpar buffers, etc
