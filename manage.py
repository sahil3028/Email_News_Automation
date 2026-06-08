import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "email_news_automation.settings")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    main()
