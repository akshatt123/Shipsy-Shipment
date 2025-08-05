#!/bin/bash

echo "🚀 Deploying Flask Task Manager to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel:"
    vercel login
fi

# Set environment variables
echo "⚙️ Setting environment variables..."
vercel env add SECRET_KEY production << EOF
your-super-secret-key-here-change-this
EOF

# Deploy to production
echo "🚀 Deploying to production..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at the URL shown above."
