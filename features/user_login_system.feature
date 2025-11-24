Feature: User Login System

  Scenario: Successful login with valid credentials
    Given the user is on the login page
    When the user enters valid username and password
    Then the system redirects to the dashboard