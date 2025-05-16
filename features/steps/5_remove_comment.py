from behave import given, when, then
from splinter.exceptions import ElementDoesNotExist
import time

# Comment removal specific steps
@given('I have submitted a comment "{comment_text}" with {stars:d} stars')
def step_impl(context, comment_text, stars):
    # Reuse existing steps to submit a comment
    context.execute_steps(f'''
        Given I am on the dashboard
        When I search for "Julio Iglesias"
        And I click on a media result for "Julio Iglesias"
        And I enter "{comment_text}" into the comment textarea
        And I select {stars} stars
        And I submit the comment form
    ''')
    # Verify the comment exists before removal test
    context.execute_steps(f'''
        Then I should see the comment "{comment_text}"
        And the comment should have a {stars}-star rating
    ''')
    # Verify remove button is visible after submission
    remove_btn = context.browser.find_by_id('remove-comment-btn').first
    assert not remove_btn.has_class('hidden'), "Remove button not visible after submission"


@when('I click the remove comment button')
def step_impl(context):
    # Wait for button to be interactable
    remove_btn = context.browser.find_by_id('remove-comment-btn').first
    remove_btn.scroll_to()

    # Double-check visibility
    if remove_btn.has_class('hidden'):
        raise ElementDoesNotExist("Remove button is hidden when trying to click")

    # Click and wait for action to complete
    remove_btn.click()

    # Wait for either:
    # 1. Comment to disappear
    # 2. Remove button to hide
    start_time = time.time()
    while time.time() - start_time < 10:
        if not context.browser.is_text_present("Temporary comment"):
            break
        if context.browser.find_by_id('remove-comment-btn').first.has_class('hidden'):
            break
        time.sleep(0.5)
    else:
        raise AssertionError("Remove action didn't complete within 10 seconds")


@then('I should not see the comment "{comment_text}"')
def step_impl(context, comment_text):
    # Wait for comment to disappear
    context.browser.is_text_not_present(comment_text, wait_time=10)

    # Additional check for comment container removal
    if context.browser.is_element_present_by_css('.test-comment-container'):
        raise AssertionError("Comment container still exists in DOM")


@then('the remove button should be hidden')
def step_impl(context):
    # Check button state
    remove_btn = context.browser.find_by_id('remove-comment-btn').first
    assert remove_btn.has_class('hidden'), "Remove button still visible after deletion"

    # Verify form reset
    textarea = context.browser.find_by_id('comment-text').first
    assert textarea.value == '', "Textarea not cleared after removal"

    # Verify star rating reset
    rating_input = context.browser.find_by_id('star-rating').first
    assert rating_input.value == '0', "Star rating not reset after removal"