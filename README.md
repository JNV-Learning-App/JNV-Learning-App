# JNV Learning App
Mobile-friendly Flask + SQLite starter app.

## Run
1. Python 3.10+ install karein.
2. `pip install -r requirements.txt`
3. `python app.py`
4. Browser: http://127.0.0.1:5000

Admin demo:
- ID: admin
- Password: admin123
- Production me password/secret key turant change karein.

## Included
- Student registration/login
- Parent mobile field
- Gujarati / English / Hindi test selection
- Random question paper
- Server-side scoring using only submitted question IDs
- Result history and average progress
- Admin-only dashboard
- Basic API progress endpoint

## WhatsApp
`whatsapp_config.example.json` me configuration template diya hai. Real automatic WhatsApp messaging ke liye authorized WhatsApp Business/Cloud API credentials aur approved templates add karne honge. This starter does not pretend to send messages without credentials.

## Note
Sample question bank chhota hai. Production JNV question bank ko verified, blueprint-aligned questions se populate karein. Current official JNVST notice/syllabus ke hisaab se blueprint ko configurable rakhein.

## PWA
The app now includes a Web App Manifest, service worker and installable icons.
For production installation, serve the app over HTTPS (except localhost). On Android Chrome, open the hosted URL and use "Install app" / "Add to Home screen".
