Feature: Reserva e manutenção de reservas
    As a usuário autenticado no sistema
    I want to criar, visualizar, editar e cancelar reservas de salas
    So that eu possa organizar o uso dos espaços disponíveis conforme minha necessidade


    Scenario: Realizar reserva de sala com sucesso
        Given eu estou na página "Nova Reserva" logado como usuário autenticado
        And os campos "Sala", "Horário de início" e "Horário de fim" estão vazios
        And a sala "Sala A" não possui reserva confirmada no dia 20/06/2025 entre 10h e 12h
        When eu seleciono a sala "Sala A"
        And eu preencho o campo "Horário de início" com "20/06/2025 10:00"
        And eu preencho o campo "Horário de fim" com "20/06/2025 12:00"
        And eu clico em "Confirmar reserva"
        Then eu vejo a mensagem "Reserva criada com sucesso! Aguardando confirmação do administrador."
        And a reserva aparece na minha listagem com status "Pendente"
        And as informações exibidas são: nome "Sala A", data "20/06/2025", início "10:00", fim "12:00", status "Pendente"
      
    Scenario: Tentar reservar sala com conflito de horário
        Given eu estou na página "Nova Reserva" logado como usuário autenticado
        And a sala "Sala B" possui reserva com status "Confirmada" no dia 21/06/2025 entre 14h e 16h
        When eu seleciono a sala "Sala B"
        And eu preencho o campo "Horário de início" com "21/06/2025 14:00"
        And eu preencho o campo "Horário de fim" com "21/06/2025 16:00"
        And eu clico em "Confirmar reserva"
        Then eu vejo a mensagem de erro "Conflito de horário: a sala já está reservada neste período."
        And nenhuma nova reserva é criada no sistema
  
    Scenario: Editar reserva pendente com sucesso
      Given eu estou na página "Minhas Reservas" logado como usuário autenticado
      And eu possuo uma reserva da "Sala C" no dia 22/06/2025 das 09h às 11h com status "Pendente"
      And a "Sala C" não possui reserva confirmada no dia 22/06/2025 entre 11h e 13h
      When eu clico em "Editar" na reserva da "Sala C"
      And eu altero o campo "Horário de início" para "22/06/2025 11:00"
      And eu altero o campo "Horário de fim" para "22/06/2025 13:00"
      And eu clico em "Salvar alterações"
      Then eu vejo a mensagem "Reserva atualizada com sucesso!"
      And a reserva aparece na listagem com horário "11:00 – 13:00" e status "Pendente"
  
    Scenario: Cancelar reserva pendente
      Given eu estou na página "Minhas Reservas" logado como usuário autenticado
      And eu possuo uma reserva da "Sala D" no dia 23/06/2025 das 08h às 10h com status "Pendente"
      When eu clico em "Cancelar" na reserva da "Sala D"
      And eu confirmo o cancelamento no diálogo exibido
      Then eu vejo a mensagem "Reserva cancelada com sucesso."
      And a reserva da "Sala D" não aparece mais na minha listagem de reservas
      And o sistema envia um email de confirmação de cancelamento para o usuário


    Scenario: Tentar reservar sala já ocupada
        Given eu estou na página "Nova Reserva" logado como usuário autenticado
        And a sala "Sala E" já possui uma reserva confirmada no dia 24/06/2025 entre 15h e 17h
        When eu seleciono a sala "Sala E"
        And eu preencho o campo "Horário de início" com "24/06/2025 15:00"
        And eu preencho o campo "Horário de fim" com "24/06/2025 17:00"
        And eu clico em "Confirmar reserva"
        Then o sistema exibe a mensagem "Sala não disponível para o período selecionado"
        And nenhuma reserva é criada

    Scenario: Tentar reservar sem estar logado
        Given eu não estou logado no sistema
        When eu tento acessar a página "Nova Reserva"
        Then o sistema me redireciona para a página de login
        And eu vejo a mensagem "Você deve estar logado para fazer uma reserva"



   
