@echo off
REM Prepare repository for Hugging Face deployment

echo 🚀 Preparing for Hugging Face deployment...

REM Backup original README
if exist "README.md" (
    echo 📝 Backing up original README.md to README_LOCAL.md
    move /Y README.md README_LOCAL.md
)

REM Use Hugging Face README
echo 📝 Setting up Hugging Face README
move /Y README_HF.md README.md

echo.
echo ✅ Done! Your repository is ready for Hugging Face.
echo.
echo Next steps:
echo 1. Create a new Space on Hugging Face
echo 2. Push your code: git push hf main
echo 3. Configure secrets in Space settings
echo.
echo See DEPLOYMENT_GUIDE.md for detailed instructions.
pause
