Feature: maintenance
  As a teacher at an institution
  I want to add, remove, or edit room maintenance requests
  so that I can report and follow up on room issues that affect my classes

  Scenario: Criar solicitação de manutenção com sucesso 
    Given o professor autenticado acessa o formulário de nova solicitação 
    And nenhuma solicitação sua existe para a sala informada 
    When o professor informa "Grad 2" no campo "Nome da sala" 
    And o professor informa "Ar-condicionado com defeito" no campo "Descrição"
    Then o sistema registra a solicitação com status "Pendente" associada ao professor autenticado 
    And o sistema retorna confirmação de sucesso

mudando a linha