Feature: User Login via Spotify

  Scenario: User logs in with valid Spotify credentials
    Given I am on the homepage
    When I click the "Login with Spotify" button
    And I log in to Spotify with test credentials
    Then I should be redirected to the dashboard