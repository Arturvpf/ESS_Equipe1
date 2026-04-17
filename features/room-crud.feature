
Scenario: Criar Sala
Given eu estou logado como administrador com o usuário “Maria” com CPF “111111” 
And eu estou na tela de salas cadastradas
And a sala de nome “D005” não aparece na lista de salas cadastradas
When eu seleciono a opção “cadastrar sala”
And tento cadastrar a sala “D005” com capacidade “80”, descrição com “sala de reunião”, número de computadores “40” e status de manutenção “Não”
Then eu vejo uma mensagem de confirmação de cadastro de sala 
And eu ainda estou na tela de salas cadastradas
And eu vejo a sala “D005” na lista de salas cadastradas

Scenario: Remover Sala
Given eu estou logado como administrador com o usuário “Maria” com CPF “111111” 
And eu estou na tela de salas cadastradas
And eu vejo a sala “D005” na lista de salas cadastradas
When eu seleciono a opção “remover sala” da sala “D005”
And confirmo que realmente quero remover a sala “D005”
Then eu vejo uma mensagem de confirmação de remoção de sala
And eu ainda estou na tela de salas cadastradas
And eu não vejo a sala “D005” na lista de salas cadastradas

Scenario: Editar Sala
Given eu estou logado como administrador com o usuário “Maria” com CPF “111111” 
And eu estou na tela de salas cadastradas
And eu vejo a sala “D005” na lista de salas cadastradas com capacidade “80”
When eu seleciono a opção “editar sala” da sala “D005”
And edito a capacidade “80” para “60” 
And salvo as alterações
Then eu recebo uma mensagem de confirmação de edição
And eu ainda estou na tela de salas cadastradas
And a sala “D005” aparece com capacidade “60” na lista de salas cadastradas

Scenario: Tentar criar sala duplicada
Given eu estou logado como administrador com o usuário “Maria” com CPF “111111” 
And eu estou na tela de salas cadastradas
And eu vejo a sala “D005” na lista de salas cadastradas
When eu seleciono a opção “cadastrar sala”
And tento cadastrar a sala “D005” com capacidade “80”, descrição com “sala de reunião”, número de computadores “30” e status de manutenção “Não”
Then eu recebo uma mensagem de erro informando que a sala “D005” já existe
And eu continuo na tela com o formulário de cadastro de sala 
And a tela do formulário de cadastro está com todos os campos vazios

Scenario: Remover Sala Reservada
Given eu estou logado como administrador com o usuário “Maria” com CPF “111111” 
And eu estou na tela de salas cadastradas
And eu vejo a sala “D005” na lista de salas cadastradas 
And eu vejo que a sala "D005" está reservada
When eu seleciono a opção “remover sala” da sala “D005”
Then eu vejo uma mensagem de erro informando que não posso remover uma sala reservada
And eu ainda estou na tela de salas cadastradas
And eu continuo vendo a sala “D005” na lista de salas cadastradas

Scenario: Tentar Editar Sala Reservada
Given eu estou logado como administrador com o usuário “Maria” com CPF “111111” 
And eu estou na tela de salas cadastradas
And eu vejo a sala “D005” na lista de salas cadastradas com capacidade “80”
When eu seleciono a opção “editar sala” da sala “D005”
Then eu recebo uma mensagem de erro informando que não é possível editar uma sala reservada
And eu ainda estou na tela de salas cadastradas
And a sala “D005” ainda aparece com capacidade “80” na lista de salas cadastradas