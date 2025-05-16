from behave import given, when, then
from django.urls import reverse
import time


def get_url(path):
    return f"http://127.0.0.1:8000{path}"


@given('I am on the homepage')
def step_impl(context):
    spotify_email = context.config.userdata.get('SPOTIFY_EMAIL')
    spotify_password = context.config.userdata.get('SPOTIFY_PASSWORD')
    print(f"Email: {spotify_email}, Password: {spotify_password}")
    context.browser.visit(get_url(reverse('landing')))


@when('I click the "{button_text}" button')
def step_impl(context, button_text):
    context.browser.find_by_text(button_text).first.click()


@when('I log in to Spotify with test credentials')
def step_impl(context):
    spotify_email = context.config.userdata.get('SPOTIFY_EMAIL')
    spotify_password = context.config.userdata.get('SPOTIFY_PASSWORD')

    # Handle email entry page
    context.browser.is_element_present_by_css('input[data-testid="login-username"]', wait_time=10)
    email_field = context.browser.find_by_css('input[data-testid="login-username"]').first
    email_field.fill(spotify_email)

    time.sleep(4)

    # Click Continue button
    continue_button = context.browser.find_by_css('button[data-testid="login-button"]').first
    continue_button.click()

    time.sleep(2)

    # Click "Log in with a password" button
    context.browser.is_element_present_by_text('Log in with a password', wait_time=10)
    context.browser.find_by_text('Log in with a password').first.click()

    time.sleep(1)

    # Handle password page
    context.browser.is_element_present_by_css('input[data-testid="login-password"]', wait_time=10)
    password_field = context.browser.find_by_css('input[data-testid="login-password"]').first
    password_field.fill(spotify_password)

    time.sleep(4)

    # Click Log In button
    login_button = context.browser.find_by_css('button[data-testid="login-button"]').first
    login_button.click()

    time.sleep(1)

    # Handle possible consent screen
    if context.browser.is_text_present('Agree', wait_time=5):
        context.browser.find_by_text('Agree').first.click()


@then('I should be redirected to the dashboard')
def step_impl(context):
    expected_url = get_url(reverse('dashboard'))
    start_time = time.time()
    while time.time() - start_time < 10:
        if context.browser.url == expected_url:
            return
        time.sleep(0.5)
    assert False, f"Not redirected to dashboard. Current URL: {context.browser.url}"
