Feature: Comment Submission

  Scenario: Submit a comment with rating on media item
    Given I am logged in
    And I search for "Julio Iglesias"
    And I am viewing the media detail for "Julio Iglesias"
    When I enter "This album is fantastic!" into the comment textarea
    And I select 5 stars
    And I submit the comment form
    Then I should see the comment "This album is fantastic!"
    And the comment should have a 5-star rating