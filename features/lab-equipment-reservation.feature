Feature: Lab equipment reservation

  As an enrolled student
  I want to reserve computers in a laboratory room
  So that I can guarantee access to the equipment at the desired time

  Scenario: Successful equipment reservation
    Given I am logged into the system as student "Vitoria"
    And I am on the "New Reservation" page
    And the room "Lab A" is available
    When I fill in the room name with "Lab A"
    And I fill in the number of computers with "3"
    And I fill in the start time with "10/04/2026 08:00"
    And I fill in the end time with "10/04/2026 10:00"
    And I click on "Confirm"
    Then I see the message "Reservation sent successfully"
    And the reservation is created with status "Pending"

  Scenario: Attempt to reserve equipment in a room under maintenance
    Given I am logged into the system as student "Vitoria"
    And I am on the "New Reservation" page
    And the room "Lab B" is under maintenance
    When I fill in the room name with "Lab B"
    And I fill in the number of computers with "2"
    And I fill in the start time with "10/04/2026 14:00"
    And I fill in the end time with "10/04/2026 16:00"
    And I click on "Confirm"
    Then I see the error message "Room under maintenance. Reservation not allowed"
    And no reservation is created

  Scenario: Attempt to create a reservation with a time conflict for the same student
    Given I am logged into the system as student "Vitoria"
    And I already have a reservation from "10/04/2026 08:00" to "10/04/2026 10:00"
    And I am on the "New Reservation" page
    When I fill in the room name with "Lab A"
    And I fill in the number of computers with "1"
    And I fill in the start time with "10/04/2026 09:00"
    And I fill in the end time with "10/04/2026 11:00"
    And I click on "Confirm"
    Then I see the error message "You already have a reservation at this time"
    And no reservation is created

  Scenario: Cancel a pending reservation
    Given I am logged into the system as student "Vitoria"
    And I have a reservation for room "Lab A" with status "Pending"
    And I am on the reservation details page
    When I click on "Cancel"
    Then the reservation is canceled successfully
    And the reservation no longer appears in my active reservations list

  Scenario: Successful reservation creation service scenario
    Given the student with login "Vitoria" has no reservation from "10/04/2026 08:00" to "10/04/2026 10:00"
    And the room "Lab A" is not under maintenance
    When the system receives a reservation request with room "Lab A", number of computers "3", start time "10/04/2026 08:00", and end time "10/04/2026 10:00" for the student with login "Vitoria"
    Then the system registers the reservation with status "Pending"
    And the reservation is associated with the student with login "Vitoria"
    And the stored data are room "Lab A", 3 computers, start time "10/04/2026 08:00", and end time "10/04/2026 10:00"

  Scenario: Block reservation in a room under maintenance
    Given the student with login "Vitoria" has no reservation from "10/04/2026 14:00" to "10/04/2026 16:00"
    And the room "Lab B" is under active maintenance
    When the system receives a reservation request with room "Lab B", number of computers "2", start time "10/04/2026 14:00", and end time "10/04/2026 16:00" for the student with login "Vitoria"
    Then the system does not register any reservation
    And the system returns the error "The room 'Lab B' is under maintenance and cannot be reserved"