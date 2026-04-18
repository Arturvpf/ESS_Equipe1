Scenario: Cadastro de usuário discente realizado com sucesso
Given eu estou na página “Cadastro de Usuário”
And o CPF "123.456.789-00" não está cadastrado no sistema
When eu preencho “Nome” com “Kauanny Barros”
And eu preencho “CPF” com “123.456.789-00”
And eu seleciono “Discente” como tipo de vínculo
And eu preencho “Curso” com "Engenharia da Computação”
And eu preencho “Matrícula” com “2023001234”
And eu preencho “Senha” com “senha123”
And eu clico no botão “Confirmar”
Then eu vejo uma mensagem “Usuário cadastrado com sucesso!”
And o usuário "Kauanny Barros" é cadastrado como discente no sistema
And eu sou redirecionado para a página "Login"

Scenario: Alteração de nome do usuário com sucesso
Given eu estou na página “Dados do Usuário”
And eu estou autenticado como o usuário “Kauanny Barros”
When eu clico no botão "Editar"
And eu altero o campo “Nome” para “Kauanny K. Barros”
And eu preencho o campo “Senha” com “senha123”
And eu clico no botão “Salvar alterações”
Then eu vejo uma mensagem “Dados atualizados com sucesso!”
And eu vejo o nome atualizado como “Kauanny K. Barros”
And o nome do usuário é atualizado para “Kauanny K. Barros” no sistema

Scenario: Desativação de conta com cancelamento de reservas
Given eu estou na página “Dados do Usuário”
And eu estou autenticado como o usuário “Kauanny Barros”
And o usuário possui reservas com status “Confirmada” e “Pendente”
When eu clico na opção “Desativar conta”
And eu confirmo a desativação
Then eu vejo a mensagem “Conta desativada com sucesso!”
And a conta do usuário está com status “Desativada”
And as reservas com status "Confirmada" do usuário são canceladas
And as reservas com status "Pendente" do usuário são canceladas

Scenario: Login realizado com sucesso
Given existe um usuário cadastrado com CPF "123.456.789-00"
And a senha é "senha123"
When eu informo CPF "123.456.789-00" e senha "senha123"
And eu clico em “Entrar”
Then eu sou redirecionado para a página "Home"

Scenario: Erro ao alterar dados com senha incorreta
Given eu estou na página "Dados do Usuário"
And eu estou autenticado como o usuário “Kauanny Barros”
When eu clico no botão "Editar"
And eu altero o campo "Nome" para "Kauanny K. Barros"
And eu preencho o campo “Senha” com “senhaErrada”
And eu clico no botão “Salvar alterações”
Then eu vejo a mensagem “Senha incorreta.”
And os dados não são alterados