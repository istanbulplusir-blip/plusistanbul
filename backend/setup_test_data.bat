@echo off
echo Setting up test data for Peykan Tourism Platform...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the test data creation command
python manage.py create_test_data

echo.
echo Test data setup completed!
pause 