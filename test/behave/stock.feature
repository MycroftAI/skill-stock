@xfail
Feature: mycroft-stock

  Scenario: what is microsoft trading at
    Given an english speaking user
     When the user says "what price is microsoft trading at"
     Then "mycroft-stock" should reply with dialog from "stock.price.dialog"

  Scenario Outline: stock price of microsoft
    Given an english speaking user
     When the user says "what is the stock price of <some company>"
     Then "mycroft-stock" should reply with dialog from "stock.price.dialog"

    Examples:
      | some company |
      | microsoft |
      | at&t |
      | google |
      | ibm |
      | cisco |
      | apple |
