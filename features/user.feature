Scenario: Cadastro de usuário discente realizado com sucesso
  Given eu estou na página "Cadastro"
  When eu preencho "Nome" com "Kauanny Barros"
  And eu preencho "CPF" com "123.456.789-00"
  And eu seleciono "Discente" como tipo de vínculo
  And eu preencho "Curso" com "Engenharia da Computação"
  And eu preencho "Matrícula" com "2023001234"
  And eu preencho "Senha" com "senha123"
  And eu seleciono "Confirmar"
  Then eu vejo uma mensagem "Usuário cadastrado com sucesso!"
  And o usuário "Kauanny Barros" é cadastrado como discente no sistema
  And eu sou redirecionado para a página "Login"

Scenario: Erro no cadastro de usuário discente por campo obrigatório não preenchido
  Given eu estou na página "Cadastro"
  When eu preencho "Nome" com "Kauanny Barros"
  And eu seleciono "Discente" como tipo de vínculo
  And eu preencho "Curso" com "Engenharia da Computação"
  And eu preencho "Matrícula" com "2023001234"
  And eu preencho "Senha" com "senha123"
  And eu preencho "Confirmar senha" com "senha123"
  And eu seleciono "Confirmar"
  Then eu vejo uma mensagem de erro "Todos os campos devem ser preenchidos"
  And eu continuo na página "Cadastro"

Scenario: Alteração de nome do usuário com sucesso
  Given eu estou na página "Meus Dados"
  And eu estou autenticado como o usuário de CPF "123.456.789-00" e senha "senha123"
  When eu seleciono "Editar"
  And eu altero o campo "Nome" para "Kauanny K. Barros"
  And eu preencho "Senha" com "senha123"
  And eu seleciono "Salvar alterações"
  Then eu vejo uma mensagem "Dados atualizados com sucesso!"
  And eu vejo o nome atualizado como "Kauanny K. Barros"
  And o nome do usuário é atualizado para "Kauanny K. Barros" no sistema

Scenario: Desativação de conta com cancelamento de reservas
  Given eu estou na página "Meus Dados"
  And eu estou autenticado como o usuário de CPF "123.456.789-00" e senha "senha123"
  And eu possuo uma reserva com status "Confirmada"
  And eu possuo uma reserva com status "Pendente"
  When eu seleciono "Desativar conta"
  And eu confirmo a desativação
  Then eu vejo a mensagem "Conta desativada com sucesso!"
  And a conta do usuário com CPF "123.456.789-00" passa a ter status "Desativada"
  And as reservas do usuário com status "Confirmada" passam a ter status "Cancelada"
  And as reservas do usuário com status "Pendente" passam a ter status "Cancelada"
  And eu sou redirecionado para a página "Login"

Scenario: Login realizado com sucesso
  Given existe um usuário cadastrado com CPF "123.456.789-00" e senha "senha123"
  And eu estou na página "Login"
  When eu preencho CPF "123.456.789-00" e senha "senha123"
  And eu seleciono "Entrar"
  Then eu sou redirecionado para a página "Home"
  And eu vejo meu nome na página inicial

Scenario: Erro ao alterar dados com senha incorreta
  Given eu estou autenticado como o usuário de CPF "123.456.789-00" e senha "senha123"
  And eu estou na página "Meus Dados"
  When eu seleciono "Editar"
  And eu altero o campo "Nome" para "Kauanny K. Barros"
  And eu preencho "Senha" com "senhaErrada"
  And eu seleciono "Salvar alterações"
  Then eu vejo a mensagem "Senha incorreta."
  And o nome do usuário permanece como "Kauanny Barros"


Scenario: Tentativa de cadastro com CPF já existente
  Given eu estou na página "Cadastro"
  And o CPF "123.456.789-00" já está cadastrado no sistema
  When eu preencho "Nome" com "Kauanny Barros"
  And eu preencho "CPF" com "123.456.789-00"
  And eu seleciono "Discente" como tipo de vínculo
  And eu preencho "Curso" com "Engenharia da Computação"
  And eu preencho "Matrícula" com "2023005678"
  And eu preencho "Senha" com "senha123"
  And eu seleciono "Confirmar"
  Then eu vejo a mensagem "CPF já cadastrado no sistema."
  And eu permaneço na página "Cadastro"

Scenario: Erro de login com CPF não cadastrado
  Given não existe usuário cadastrado com CPF "111.111.111-11"
  And eu estou na página "Login"
  When eu preencho "CPF" com "111.111.111-11"
  And eu preencho "Senha" com "senha123"
  And eu seleciono "Entrar"
  Then eu vejo a mensagem "CPF ou senha incorretos."
  And eu permaneço na página "Login"

Scenario: Tentativa de alteração de nome com campo vazio
  Given eu estou autenticado como o usuário de CPF "123.456.789-00" e senha "senha123"
  And eu estou na página "Meus Dados"
  When eu seleciono "Editar"
  And eu limpo o campo "Nome"
  And eu preencho "Senha" com "senha123"
  And eu seleciono "Salvar alterações"
  Then eu vejo a mensagem "O campo Nome não pode ser vazio."
  And os dados não são alterados no sistema
