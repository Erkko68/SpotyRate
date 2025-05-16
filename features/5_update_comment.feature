Feature: Comment Update

  Scenario: Update existing comment
    Given I am logged in
    And I search for "Julio Iglesias"
    And I am viewing the media detail for "Julio Iglesias"

    # Existing comment
    When I enter "Initial review text" into the comment textarea
    And I select 4 stars
    And I submit the comment form
    Then I should see the comment "Initial review text"
    And the comment should have a 4-star rating

    # Update comment
    When I enter "Updated review text" into the comment textarea
    And I select 2 stars
    And I submit the comment form
    Then I should see the comment "Updated review text"
    And the comment should have a 2-star rating