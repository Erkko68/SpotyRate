Feature: Search functionality

  Scenario: User searches for an artist and views results
    Given I am on the dashboard
    When I search for "Julio Iglesias"
    Then I should see media information for "Julio Iglesias"
