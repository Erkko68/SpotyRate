from behave import given, when, then
from splinter.exceptions import ElementDoesNotExist
import time


@given('I am viewing the media detail for "{term}"')
def step_impl(context, term):
    context.execute_steps(f'''
        Given I am logged in
        And I search for "{term}"
        When I click on a media result for "{term}"
    ''')
    context.browser.is_element_present_by_css('.media-detail-container', wait_time=10)


@when('I enter "{comment_text}" into the comment textarea')
def step_impl(context, comment_text):
    textarea = context.browser.find_by_id('comment-text').first
    textarea.fill(comment_text)


@when('I select {stars:d} stars')
def step_impl(context, stars):
    # Wait for stars to be present
    context.browser.is_element_present_by_css('.star', wait_time=10)

    # Find using CSS selector instead of XPath
    star_element = context.browser.find_by_css(
        f'.star[data-value="{stars}"]'
    ).first

    # Scroll into view and click
    star_element.scroll_to()
    star_element.click()

    # Verify rating input was updated
    rating_input = context.browser.find_by_id('star-rating').first
    assert rating_input.value == str(stars), \
        f"Expected rating {stars}, got {rating_input.value}"


@when('I submit the comment form')
def step_impl(context):
    # Wait for form to be present
    context.browser.is_element_present_by_id('comment-form', wait_time=10)

    # Find the submit button using more specific selector
    submit_button = context.browser.find_by_css(
        '#comment-form button[type="submit"]'
    ).first

    # Scroll into view and click
    submit_button.scroll_to()
    submit_button.click()

    # Wait for either:
    # 1. The form to reset (textarea cleared)
    # 2. Or the comment to appear in the list
    # 3. Or an error message to appear
    start_time = time.time()
    while time.time() - start_time < 10:  # Wait up to 10 seconds
        textarea = context.browser.find_by_id('comment-text').first
        if textarea.value == '':  # Form was reset
            break
        if context.browser.is_text_present('This album is fantastic!'):  # Comment appeared
            break
        if context.browser.is_element_present_by_css('.error-message:not(.hidden)'):  # Error shown
            break
        time.sleep(0.5)
    else:
        raise AssertionError("Form submission didn't complete within 10 seconds")


@then('I should see the comment "{comment_text}"')
def step_impl(context, comment_text):
    assert context.browser.is_text_present(comment_text, wait_time=10), \
        f"Comment text '{comment_text}' not found on page"


@then('the comment should have a {stars:d}-star rating')
def step_impl(context, stars):
    # Wait for comment container with test-specific class
    context.browser.is_element_present_by_css('.test-comment-container', wait_time=10)

    # Get all comment containers
    comments = context.browser.find_by_css('.test-comment-container')
    assert comments, "No comments found on the page"

    # Get the most recent comment (last in list)
    latest_comment = comments.last

    # Find the star rating container within the comment
    rating_container = latest_comment.find_by_xpath(
        './/div[contains(@class, "flex") and contains(@class, "items-center") and contains(@class, "gap-1")]'
    ).first

    # Count filled stars using text content
    filled_stars = len(rating_container.find_by_xpath('.//span[text()="★"]'))

    assert filled_stars == stars, \
        f"Expected {stars} filled stars, found {filled_stars}"