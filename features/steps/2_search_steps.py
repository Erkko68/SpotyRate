from behave import given, when, then

@given('I am on the dashboard')
def step_impl(context):
    assert "dashboard" in context.browser.url, f"Expected to be on dashboard, but was at {context.browser.url}"

@given('I search for "{term}"')
@when('I search for "{term}"')
def step_impl(context, term):
    search_input = context.browser.find_by_css('input[name="q"]').first
    search_input.fill(term)
    search_input.type("\n")
    context.browser.is_element_present_by_text(f'Search Results for “{term}”', wait_time=10)

@then('I should see media information for "{term}"')
def step_impl(context, term):
    assert context.browser.is_text_present(term, wait_time=10), f"Media info for '{term}' not found."
