from behave import given, when, then
from splinter.exceptions import ElementDoesNotExist
import time

@given("I am logged in")
def step_impl(context):
    context.browser.visit("http://127.0.0.1:8000/dashboard/")

    if "Login with Spotify" in context.browser.html:
        # Not logged in — go through login flow
        context.browser.visit("http://127.0.0.1:8000/")
        context.browser.find_by_text("Login with Spotify").first.click()

        email_field = context.browser.find_by_css('input[data-testid="login-username"]').first
        password_field = context.browser.find_by_css('input[data-testid="login-password"]').first

        email_field.fill("spotyratedemo@gmail.com")
        password_field.fill("WebProject2025")

        context.browser.find_by_css('button[data-testid="login-button"]').first.click()

    context.browser.is_element_present_by_text("Your Dashboard", wait_time=10)

# Here, use {term} as a placeholder in the decorator, not hardcoded string:
@when('I click on a media result for "{term}"')
def step_impl(context, term):
    # Wait until search results container is present
    context.browser.is_element_present_by_css("#search-results", wait_time=10)

    try:
        media_result = context.browser.find_by_css(".result-item").first
        media_result.click()
    except ElementDoesNotExist:
        raise AssertionError(f"No media result was found for term: {term}")

    # Wait for media detail page to load - check for unique detail page element or URL change
    # Example: wait for media title or URL containing some media ID
    if not context.browser.is_element_present_by_css(".text-4xl.font-bold", wait_time=10):
        raise AssertionError("Media detail page did not load after clicking media result")

    # Optional: assert URL has changed if your media detail URLs differ
    # assert "media" in context.browser.url, f"Expected media detail page URL, got {context.browser.url}"


@then('I should see detailed media information for "{term}"')
def step_impl(context, term):
    time.sleep(5)
    assert context.browser.is_element_present_by_css(".text-4xl.font-bold", wait_time=10), \
        "Media title was not found on detail view"

    assert context.browser.is_element_present_by_css(".result-item.track-item"), \
        "No tracks were displayed in the media detail view"
