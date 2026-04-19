
Cenário 1: Listagem de reservas com filtro por status
O usuário acessa a listagem e aplica um filtro por status (ex: "Pendente"). 
O sistema exibe apenas as reservas com aquele status, mostrando nome da sala,
 data, hora início/fim e status de cada uma E SE houve objetos/instrumentos reservados.


Cenário 2: Edição de reserva pendente a partir da listagem
O usuário visualiza a listagem e clica em "Editar" em uma reserva 
com status Pendente. O sistema abre o formulário de edição. Para reservas Confirmadas, Negadas ou Concluídas, o botão de edição deve estar desabilitado.

Cenário 3: Remoção de reserva pendente a partir da listagem
O usuário clica em "Remover" em uma reserva pendente. O sistema
pede confirmação e, após confirmação, remove a reserva da listagem.
Botão desabilitado para outros status.

Cenário 4: Ordenação padrão e exibição de informações completas
O usuário acessa a listagem sem nenhum filtro. O sistema exibe 
todas as reservas dele, ordenadas *da mais recente para a mais
antiga *, com as informações: nome da sala, data, hora início/fim, 
status e (quando houver) número de computadores reservados.

Cenário 5: Checar status de uma sala reservada
O usuário acessa a página da listagem de reservas e o sistema exibe 
todas as reservas realizadas por ele, mostrando para cada uma: nome da 
sala, data, hora de início e fim, status da reserva e, quando aplicável,
informações adicionais como objetos/instrumentos ou número de computadores 
reservados.
