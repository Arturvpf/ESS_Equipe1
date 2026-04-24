Feature: Verificação de Reservas e Manutenções
  As um administrador do sistema
  I want to visualizar, confirmar ou negar reservas e solicitações de manutenção
  So that eu possa gerenciar a alocação e o estado das salas adequadamente

  Scenario: Visualização da listagem com prioridade para professores
    Given eu estou logado como administrador
    When eu acesso a página de visualização de reservas e manutenções
    Then o sistema lista todas as reservas e solicitações cadastradas
    And a listagem exibe com prioridade as reservas pendentes feitas por professores

  Scenario: Confirmar uma reserva pendente com sucesso
    Given eu estou na página de visualização de reservas
    And existe uma reserva com status "Pendente"
    When eu seleciono a opção de confirmar essa reserva
    Then o status da reserva é atualizado para "Confirmada" no sistema
    And o usuário pode visualizar a mudança de status em sua própria listagem de reservas

  Scenario: Negar uma reserva pendente sem justificativa
    Given eu estou na página de visualização de reservas
    And existe uma reserva com status "Pendente"
    When eu seleciono a opção de negar essa reserva
    Then o status da reserva é atualizado para "Negada" no sistema
    And o sistema não exige ou exibe campo para preenchimento de justificativa

  Scenario: Tentativa de reverter uma reserva já decidida
    Given eu estou na página de visualização de reservas
    And uma reserva já possui o status "Confirmada" ou "Negada"
    When eu visualizo os detalhes dessa reserva
    Then as opções de confirmar e negar ficam desabilitadas
    And o sistema não permite reverter ou alterar a decisão

  Scenario: Tentativa de editar os dados de uma reserva alheia
    Given eu estou na página de visualização de reservas
    When eu visualizo uma reserva feita por um usuário
    Then o sistema não me permite editar os dados da reserva
    And eu apenas possuo permissão para confirmar ou negar

  Scenario: Confirmar manutenção e negar reservas pendentes na sala
    Given a sala "Laboratório 1" possui uma solicitação de manutenção "Pendente"
    And a sala "Laboratório 1" possui reservas com status "Pendente"
    When eu confirmo a solicitação de manutenção
    Then a solicitação de manutenção passa para o status "Confirmada"
    And a sala "Laboratório 1" entra em manutenção
    And o sistema altera automaticamente todas as reservas pendentes dessa sala para "Negada"
    And nenhuma nova reserva pode ser feita para esta sala

  Scenario: Impedir manutenção em sala com reserva confirmada
    Given a sala "Sala de Reunião" possui uma solicitação de manutenção "Pendente"
    And a sala "Sala de Reunião" possui reservas com status "Confirmada" ainda não concluídas
    When eu tento confirmar a solicitação de manutenção para a "Sala de Reunião"
    Then o sistema impede que a sala entre em manutenção
    And o sistema informa que existem reservas confirmadas que precisam ser concluídas primeiro

  Scenario: Concluir uma manutenção em andamento
    Given a sala "Sala 10" possui uma solicitação de manutenção com status "Confirmada" (em andamento)
    When eu registro que a manutenção foi finalizada
    Then a solicitação de manutenção passa para o status "Concluída"
    And a sala "Sala 10" volta a ficar disponível para novas reservas