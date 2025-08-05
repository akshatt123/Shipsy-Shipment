"""
Deployment Guide for Vercel
This script provides step-by-step instructions for deploying the Flask app to Vercel
"""

def print_deployment_guide():
    print("=" * 70)
    print("🚀 VERCEL DEPLOYMENT GUIDE FOR FLASK TASK MANAGER")
    print("=" * 70)
    
    print("\n📋 PREREQUISITES:")
    print("1. Install Vercel CLI: npm install -g vercel")
    print("2. Create a Vercel account at https://vercel.com")
    print("3. Login to Vercel: vercel login")
    
    print("\n📁 PROJECT STRUCTURE (Required for Vercel):")
    print("├── api/")
    print("│   └── index.py          # Main entry point for Vercel")
    print("├── templates/            # Jinja2 templates")
    print("├── models/              # Database models")
    print("├── routes/              # Flask blueprints")
    print("├── utils/               # Utility functions")
    print("├── vercel.json          # Vercel configuration")
    print("└── requirements.txt     # Python dependencies")
    
    print("\n🔧 DEPLOYMENT STEPS:")
    print("1. Navigate to your project directory:")
    print("   cd your-flask-project")
    
    print("\n2. Initialize Vercel project:")
    print("   vercel")
    print("   - Follow the prompts")
    print("   - Choose 'N' for existing project")
    print("   - Set project name")
    print("   - Choose your account/team")
    
    print("\n3. Set environment variables (optional):")
    print("   vercel env add SECRET_KEY")
    print("   - Enter your secret key when prompted")
    
    print("\n4. Deploy to production:")
    print("   vercel --prod")
    
    print("\n⚙️ VERCEL.JSON CONFIGURATION:")
    print("""
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  }
}
    """)
    
    print("\n🔍 TROUBLESHOOTING COMMON ISSUES:")
    print("\n1. Import Errors:")
    print("   - Ensure all imports use absolute paths")
    print("   - Add project root to sys.path in api/index.py")
    
    print("\n2. Template Not Found:")
    print("   - Use template_folder='../templates' in Flask app")
    print("   - Ensure templates directory is at project root")
    
    print("\n3. Database Issues:")
    print("   - Use /tmp/ directory for SQLite in serverless")
    print("   - Initialize database on each cold start")
    print("   - Consider using external database for production")
    
    print("\n4. Static Files:")
    print("   - Use CDN links for CSS/JS (Bootstrap, FontAwesome)")
    print("   - Or create static/ directory and configure properly")
    
    print("\n📝 ENVIRONMENT VARIABLES:")
    print("Set these in Vercel dashboard or via CLI:")
    print("- SECRET_KEY: Your Flask secret key")
    print("- DATABASE_PATH: /tmp/tasks.db (for serverless)")
    
    print("\n🎯 TESTING DEPLOYMENT:")
    print("1. Test locally first: python api/index.py")
    print("2. Deploy to preview: vercel")
    print("3. Test preview URL thoroughly")
    print("4. Deploy to production: vercel --prod")
    
    print("\n✅ POST-DEPLOYMENT CHECKLIST:")
    print("□ Login functionality works")
    print("□ CRUD operations work")
    print("□ Filtering and pagination work")
    print("□ Database persists between requests")
    print("□ Error handling works properly")
    print("□ Mobile responsiveness")
    
    print("\n🔗 USEFUL COMMANDS:")
    print("vercel --help           # Show all commands")
    print("vercel logs             # View deployment logs")
    print("vercel env ls           # List environment variables")
    print("vercel domains          # Manage custom domains")
    print("vercel --prod           # Deploy to production")
    
    print("\n" + "=" * 70)
    print("🎉 Your Flask app should now be deployed on Vercel!")
    print("Visit your deployment URL to test the application.")
    print("=" * 70)

if __name__ == "__main__":
    print_deployment_guide()
