@echo off
echo Installing required packages for Movie Recommender...
pip install flask requests beautifulsoup4 textblob

echo.
echo Installation complete! Run the app with: python main.py
echo Then visit http://127.0.0.1:5000 in your web browser
echo.
pause