#!/bin/bash
# Prepare repository for Hugging Face deployment

echo "🚀 Preparing for Hugging Face deployment..."

# Backup original README
if [ -f "README.md" ]; then
    echo "📝 Backing up original README.md to README_LOCAL.md"
    mv README.md README_LOCAL.md
fi

# Use Hugging Face README
echo "📝 Setting up Hugging Face README"
mv README_HF.md README.md

echo "✅ Done! Your repository is ready for Hugging Face."
echo ""
echo "Next steps:"
echo "1. Create a new Space on Hugging Face"
echo "2. Push your code: git push hf main"
echo "3. Configure secrets in Space settings"
echo ""
echo "See DEPLOYMENT_GUIDE.md for detailed instructions."
