Story → Movie Finder — Ready-made package
=======================================

What is included:
- frontend/ (HTML/CSS/JS)
- backend/ (Flask app)
- manual_trending.json (created at runtime)

Features included:
- Trending movies (integrates with TMDB when TMDB_API_KEY is provided)
- Posters shown using TMDB images
- Search endpoint (/search?q=)
- /find endpoint: uses Gemini if GEMINI_API_KEY provided; otherwise returns sample result
- Admin endpoint to add manual trending items (/admin/add)

Environment variables you must set before deploying:
- GEMINI_API_KEY  (optional but required for AI accuracy)
- TMDB_API_KEY    (optional but required for real trending & posters)
- ADMIN_PASSWORD  (set to secure password; default is 'changeme')

Deployment quick steps (Replit / Render / Heroku):
1. Upload backend folder and set environment variables (GEMINI_API_KEY, TMDB_API_KEY, ADMIN_PASSWORD).
2. Install requirements (pip install -r requirements.txt).
3. Run app.py — note the exposed base URL.
4. In frontend/script.js set API_BASE to your backend URL (e.g., https://movieapi.yourdomain.com).
5. Deploy frontend to Netlify / Vercel / GitHub Pages and configure domain.

AdSense:
- Replace the ad placeholders in frontend/index.html with your AdSense code snippets.
- Make sure to follow AdSense policies (no copyrighted full movies, no encouraging piracy).

Notes:
- You will need valid API keys to get live posters and trending lists (TMDB) and accurate AI answers (Gemini).
- The admin endpoint allows inserting manual trending items via POST with JSON: {password, title, poster, year, category}

If you want, I can:
- Add a small admin HTML page to call /admin/add
- Configure a Dockerfile and Procfile for easy deploy
- Add server-side caching for TMDB responses
