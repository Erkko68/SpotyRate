Feature: Comment Management

  Scenario: Remove an existing comment
    Given I am logged in
    And I have submitted a comment "Temporary comment" with 4 stars
    When I click the remove comment button
    Then I should not see the comment "Temporary comment"
    And the remove button should be hidden