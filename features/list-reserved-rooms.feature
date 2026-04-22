
Cenário 1: Listagem de reservas com filtro por status
Given que o usuário está na página de "listagem de reservas"
When ele aplica um filtro por status (ex: "Pendente")
Then o sistema exibe apenas as reservas com o status selecionado,
mostrando nome da sala, data, hora de início/fim e status de cada uma
And quando houver objetos/instrumentos reservados, essas informações também são exibidas

Cenário 2: Edição de reserva pendente a partir da listagem
Given que o usuário está na página de  "listagem de reservas"
And existe ao menos uma reserva com status "Pendente"
When ele clica no botão "Editar" de uma reserva pendente
Then o sistema abre o formulário de edição preenchido com os dados da reserva
And para reservas com status "Confirmada", "Negada" ou "Concluída", o botão "Editar" está desabilitado


Cenário 3: Remoção de reserva pendente a partir da listagem
Given que o usuário está na listagem de reservas
And existe ao menos uma reserva com status "Pendente"
When ele clica no botão "Remover" dessa reserva
Then o sistema exibe uma mensagem de confirmação
And após o usuário confirmar, a reserva é removida da listagem
And para reservas com outros status, o botão "Remover" está desabilitado


Cenário 4: Ordenação padrão e exibição de informações completas
Given que o usuário está na página de listagem de reservas
And nenhum filtro está aplicado
When a listagem é carregada
Then o sistema exibe todas as reservas do usuário ordenadas da mais recente para a mais antiga
And cada reserva exibe nome da sala, data, hora de início/fim e status
And quando houver computadores reservados, o número de computadores também é exibido

Cenário 5: Checar status de uma sala reservada
Given que o usuário está na página de listagem de reservas
When a listagem é carregada
Then o sistema exibe todas as reservas realizadas por ele
And cada reserva apresenta nome da sala, data, hora de início/fim e status
And quando aplicável, são exibidas também informações sobre objetos/instrumentos
ou número de computadores reservados
