# Feature 7 — Efetuar reserva e manutencao de reservas efetuadas (usuario)
# Aluno: Artur Vinicius Pereira Fernandes
# Persona BDD: Carlos Drummond

Feature: Efetuar reserva e manutencao de reservas efetuadas usuario
  Como um usuario autenticado do sistema Salla
  Quero criar, visualizar, editar e cancelar reservas de salas
  Para garantir que terei acesso ao espaco no horario desejado

  Scenario: Realizar reserva de sala com sucesso
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And a sala "D005" nao possui reserva confirmada no dia "2026-06-01" entre "08:00" e "10:00"
    When Carlos informa a sala "D005", horario de inicio "2026-06-01T08:00:00" e horario de fim "2026-06-01T10:00:00"
    Then a reserva e criada com status "pending"
    And a reserva aparece na listagem de Carlos com status "pending"

  Scenario: Tentar reservar sala com sobreposicao parcial de horario
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And ja existe uma reserva confirmada da sala "D005" das "2026-06-01T09:00:00" as "2026-06-01T11:00:00"
    When Carlos tenta reservar a sala "D005" das "2026-06-01T08:00:00" as "2026-06-01T10:00:00"
    Then Carlos recebe o erro "Conflito de horario: a sala ja esta reservada neste periodo"

  Scenario: Editar reserva pendente com sucesso
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos possui uma reserva pendente da sala "D005" das "2026-06-01T08:00:00" as "2026-06-01T10:00:00"
    When Carlos edita o horario de fim para "2026-06-01T11:00:00"
    Then a reserva e atualizada com horario de fim "2026-06-01T11:00:00"
    And o status da reserva permanece "pending"

  Scenario: Cancelar reserva pendente
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos possui uma reserva pendente da sala "D005" das "2026-06-02T08:00:00" as "2026-06-02T10:00:00"
    When Carlos cancela a reserva
    Then a reserva tem status "denied"

  Scenario: Tentar reservar sala ja ocupada no mesmo horario
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And ja existe uma reserva confirmada da sala "D005" das "2026-06-03T10:00:00" as "2026-06-03T12:00:00"
    When Carlos tenta reservar a sala "D005" das "2026-06-03T10:00:00" as "2026-06-03T12:00:00"
    Then Carlos recebe o erro "Conflito de horario: a sala ja esta reservada neste periodo"

  Scenario: Tentar acessar reservas sem estar autenticado
    When um usuario nao autenticado tenta listar reservas sem informar o CPF
    Then o sistema retorna erro de validacao com codigo 422

  Scenario: Exportar reserva confirmada para o Google Calendar
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos possui uma reserva com status "confirmed" da sala "D005" das "2026-06-04T14:00:00" as "2026-06-04T16:00:00"
    When Carlos solicita a exportacao da reserva para o calendario
    Then o sistema retorna um arquivo no formato iCalendar

  Scenario: Editar horario de termino de uma reserva ativa
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos possui uma reserva pendente da sala "E101" das "2026-06-05T10:00:00" as "2026-06-05T12:00:00"
    When Carlos edita apenas o horario de fim para "2026-06-05T13:00:00"
    Then a reserva e atualizada com horario de fim "2026-06-05T13:00:00"

  Scenario: Visualizar historico de reservas passadas
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos possui reservas com status "confirmed" e "denied"
    When Carlos acessa a listagem de suas reservas
    Then a listagem retorna todas as reservas de Carlos independente do status

  Scenario: Visualizar detalhes de uma reserva especifica
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos possui uma reserva pendente da sala "D005" das "2026-06-06T08:00:00" as "2026-06-06T10:00:00"
    When Carlos acessa os detalhes da reserva
    Then os detalhes exibem sala "D005", status "pending" e os horarios corretos

  Scenario: Tentar editar reserva ja confirmada
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos possui uma reserva com status "confirmed" da sala "D005" das "2026-06-07T08:00:00" as "2026-06-07T10:00:00"
    When Carlos tenta editar o horario de fim para "2026-06-07T11:00:00"
    Then Carlos recebe o erro "So e possivel editar/excluir reservas pendentes"

  Scenario: Tentar cancelar reserva ja negada
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos possui uma reserva com status "denied" da sala "D005" das "2026-06-08T08:00:00" as "2026-06-08T10:00:00"
    When Carlos tenta cancelar a reserva
    Then Carlos recebe o erro "So e possivel editar/excluir reservas pendentes"

  Scenario: Usuario tenta criar duas reservas no mesmo horario em salas diferentes
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos ja possui uma reserva pendente da sala "D005" das "2026-06-09T08:00:00" as "2026-06-09T10:00:00"
    When Carlos tenta reservar a sala "E101" das "2026-06-09T08:00:00" as "2026-06-09T10:00:00"
    Then Carlos recebe o erro "Voce ja possui uma reserva neste horario"

  Scenario: Duas reservas pending da mesma sala e horario de usuarios diferentes coexistem
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And outro usuario com CPF "98765432100" possui uma reserva pendente da sala "D005" das "2026-06-10T08:00:00" as "2026-06-10T10:00:00"
    When Carlos reserva a sala "D005" das "2026-06-10T08:00:00" as "2026-06-10T10:00:00"
    Then a reserva de Carlos e criada com status "pending"

  Scenario: Tentar exportar reserva pendente para o calendario
    Given Carlos Drummond esta autenticado no sistema com CPF "12345678901"
    And Carlos possui uma reserva pendente da sala "D005" das "2026-06-11T08:00:00" as "2026-06-11T10:00:00"
    When Carlos solicita a exportacao da reserva pendente para o calendario
    Then Carlos recebe erro informando que apenas reservas confirmadas podem ser exportadas
