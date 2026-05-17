Feature: Confirmação e Negação de Solicitações de Manutenção
  As um administrador do sistema
  I want to confirmar ou negar solicitações de manutenção de salas
  So that eu possa gerenciar adequadamente o estado e a disponibilidade das salas

  Scenario: Visualizar solicitações de manutenção pendentes
    Given eu estou logado como administrador
    When eu acesso a página de visualização de solicitações de manutenção
    And eu consigo visualizar a solicitações

  Scenario: Confirmar solicitação de manutenção com sucesso
    Given eu estou logado como administrador
    And a "Sala D005" não possui reservas com status "Confirmada" na data atual
    When eu seleciono a opção de confirmar a solicitação
    And eu preencho o campo "Data de fim da manutenção" com "26/08/2026"
    And eu clico em "Confirmar manutenção"
    Then o status da solicitação é atualizado para "Confirmada"
    And a "Sala D005" entra em manutenção com início na data atual e fim em "26/08/2026"

  Scenario: Negar solicitação de manutenção
    Given eu estou logado como administrador
    And existe uma solicitação de manutenção com status "Pendente" para a "Sala D004"
    When eu seleciono a opção de negar a solicitação
    Then o status da solicitação é atualizado para "Negada"
    And a "Sala D004" permanece disponível para reservas

  Scenario: Confirmar manutenção e negar reservas pendentes automaticamente
    Given eu estou logado como administrador
    And existe solicitação de manutenção com status "Pendente" para a "Sala D002"
    When eu seleciono a opção de confirmar a solicitação
    And eu preencho o campo "Data de fim da manutenção" com "02/07/2026"
    And eu clico em "Confirmar manutenção"
    And a "Sala D002" possui reservas com status "Pendente" dentro do período de manutenção
    Then o sistema exibe a mensagem "A sala possui reservas pendentes. Tem certeza que deseja confirmar a manutenção?"
    When eu confirmo a ação
    Then o status da solicitação é atualizado para "Confirmada"
    And todas as reservas com status "Pendente" da "Sala D002" dentro do período de manutenção foram automaticamente alteradas para "Negada"
    And a "Sala D002" entra em manutenção com início na data atual e fim em "02/07/2026"

  Scenario: Impedir confirmação de manutenção com reservas confirmadas no período
    Given eu estou logado como administrador
    And existe solicitação de manutenção com status "Pendente" para a "Sala D003"
    When eu seleciono a opção de confirmar a solicitação
    And eu preencho o campo "Data de fim da manutenção" com "19/07/2026"
    And eu clico em "Confirmar manutenção"
    Then o sistema impede a confirmação da manutenção
    And eu vejo a mensagem "Não é possível confirmar a manutenção. Existem reservas confirmadas para esta sala no período selecionado."
    And o status da solicitação permanece "Pendente"
