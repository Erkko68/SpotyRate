Feature: Media view

  Scenario: User selects a media item and sees detailed info
    Given I am logged in
    And I search for "Julio Iglesias"
    When I click on a media result for "Julio Iglesias"
    Then I should see detailed media information for "Julio Iglesias"
