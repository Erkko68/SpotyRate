import os
import django
from splinter import Browser

def before_all(context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    django.setup()

    # Initialize Splinter browser
    context.browser = Browser('chrome')
    context.browser.driver.set_window_size(1920, 1080)

def after_all(context):
    context.browser.quit()
