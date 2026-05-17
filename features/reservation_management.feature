Feature: Gerenciamento de reservas de salas
    As a Carlos Drummond, um usuário cadastrado no sistema
    I want to criar, visualizar, editar e cancelar reservas de salas
    So that organizar o uso dos espaços disponíveis conforme minha necessidade


    Scenario: Realizar reserva de sala com sucesso
        Given Carlos Drummond está na página "Nova Reserva" autenticado no sistema
        And os campos "Sala", "Horário de início" e "Horário de fim" estão vazios
        And a sala "Sala A" não possui reserva confirmada no dia 20/06/2025 entre 10h e 12h
        When Carlos informa a sala "Sala A", o horário de início "20/06/2025 10:00" e o horário de fim "20/06/2025 12:00"
        And Carlos solicita a criação da reserva
        Then Carlos vê a mensagem "Reserva criada com sucesso! Aguardando confirmação do administrador."
        And a reserva aparece na listagem de Carlos com status "Pendente"
        And as informações exibidas são: sala "Sala A", data "20/06/2025", início "10:00", fim "12:00", status "Pendente"

    Scenario: Tentar reservar sala com sobreposição parcial de horário
        Given Carlos Drummond está na página "Nova Reserva" autenticado no sistema
        And a sala "Sala B" possui reserva com status "Confirmada" no dia 21/06/2025 entre 14h e 16h
        When Carlos informa a sala "Sala B", o horário de início "21/06/2025 14:00" e o horário de fim "21/06/2025 16:00"
        And Carlos solicita a criação da reserva
        Then Carlos vê a mensagem de erro "Conflito de horário: a sala já está reservada neste período."
        And nenhuma nova reserva é criada no sistema

    Scenario: Editar reserva pendente com sucesso
        Given Carlos Drummond está na página "Minhas Reservas" autenticado no sistema
        And Carlos possui uma reserva da "Sala C" no dia 22/06/2025 das 09h às 11h com status "Pendente"
        And a sala "Sala C" não possui reserva confirmada no dia 22/06/2025 entre 11h e 13h
        When Carlos solicita a edição da reserva da "Sala C"
        And Carlos altera o horário de início para "22/06/2025 11:00"
        And Carlos altera o horário de fim para "22/06/2025 13:00"
        And Carlos confirma as alterações da reserva
        Then Carlos vê a mensagem "Reserva atualizada com sucesso!"
        And a reserva aparece na listagem com horário "11:00 – 13:00" e status "Pendente"

    Scenario: Cancelar reserva pendente
        Given Carlos Drummond está na página "Minhas Reservas" autenticado no sistema
        And Carlos possui uma reserva da "Sala D" no dia 23/06/2025 das 08h às 10h com status "Pendente"
        When Carlos solicita o cancelamento da reserva da "Sala D"
        And Carlos confirma o cancelamento
        Then Carlos vê a mensagem "Reserva cancelada com sucesso."
        And a reserva da "Sala D" não aparece mais na listagem de Carlos
        And Carlos recebe um e-mail de confirmação de cancelamento

    Scenario: Tentar reservar sala já ocupada no mesmo horário
        Given Carlos Drummond está na página "Nova Reserva" autenticado no sistema
        And a sala "Sala E" possui uma reserva confirmada no dia 24/06/2025 das 15h às 17h
        When Carlos informa a sala "Sala E", o horário de início "24/06/2025 15:00" e o horário de fim "24/06/2025 17:00"
        And Carlos solicita a criação da reserva
        Then Carlos vê a mensagem de erro "Sala não disponível para o período selecionado."
        And nenhuma nova reserva é criada no sistema

    Scenario: Tentar acessar a página de nova reserva sem estar autenticado
        Given Carlos Drummond não está autenticado no sistema
        When Carlos tenta acessar a funcionalidade de nova reserva
        Then Carlos é redirecionado para a página de login
        And Carlos vê a mensagem "Você deve estar logado para fazer uma reserva."

    Scenario: Exportar reserva confirmada para o Google Calendar
        Given Carlos Drummond está na página "Minhas Reservas" autenticado no sistema
        And Carlos possui uma reserva confirmada da "Sala F" no dia 25/06/2025 das 10h às 12h
        When Carlos solicita a exportação da reserva para o Google Calendar
        Then Carlos vê a mensagem "Reserva adicionada ao seu Google Calendar com sucesso."
        And o evento da reserva passa a constar no Google Calendar de Carlos com data "25/06/2025" e horário "10:00 – 12:00"

    Scenario: Editar horário de término de uma reserva ativa
        Given Carlos Drummond está na página "Minhas Reservas" autenticado no sistema
        And Carlos possui uma reserva ativa da "Sala G" no dia 26/06/2025 das 14h às 16h
        And a sala "Sala G" não possui reserva confirmada no dia 26/06/2025 entre 16h e 18h
        When Carlos solicita a edição da reserva da "Sala G"
        And Carlos altera o horário de fim para "26/06/2025 18:00"
        And Carlos confirma as alterações da reserva
        Then Carlos vê a mensagem "Horário alterado com sucesso!"
        And a reserva aparece na listagem com horário "14:00 – 18:00"

    Scenario: Visualizar histórico de reservas passadas
        Given Carlos Drummond está na página "Minhas Reservas" autenticado no sistema
        And Carlos possui reservas com datas anteriores ao dia de hoje registradas no sistema
        When Carlos solicita a visualização do histórico de reservas
        Then uma lista de reservas passadas é exibida com paginação
        And cada item da lista mostra data, horário, sala, status e duração

    Scenario: Visualizar detalhes de uma reserva específica
        Given Carlos Drummond está na página "Minhas Reservas" autenticado no sistema
        And Carlos possui uma reserva da "Sala A" no dia 20/06/2025 das 10h às 12h visível na listagem
        When Carlos solicita a visualização dos detalhes da reserva da "Sala A"
        Then os detalhes completos da reserva são exibidos em uma janela modal
        And as informações exibidas incluem sala, data, horário de início, horário de fim, status e nome do responsável pela reserva
