from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import os, requests, json
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Load keys from env
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
TMDB_KEY = os.environ.get("TMDB_API_KEY", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

DATA_FILE = "manual_trending.json"

def load_manual():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_manual(items):
    with open(DATA_FILE, "w") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

@app.route("/trending")
def trending():
    # Try TMDB trending + manual override
    trending = []
    most_searched = []
    if TMDB_KEY:
        try:
            tmdb = requests.get(f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_KEY}").json()
            for m in tmdb.get("results", [])[:8]:
                poster = f"https://image.tmdb.org/t/p/w300{m.get('poster_path')}" if m.get("poster_path") else ""
                trending.append({"title": m.get("title") or m.get("name"), "poster": poster, "year": (m.get('release_date') or "")[:4], "category": "Unknown"})
        except Exception as e:
            print("TMDB error", e)
    # add manual items on top
    manual = load_manual()
    trending = manual + trending
    # Most searched: a simple static list or can be enriched
    most_searched = [
        {"title":"KGF Chapter 2","poster":"https://via.placeholder.com/150x225?text=KGF2","year":2022,"category":"Bollywood"},
        {"title":"Inception","poster":"https://via.placeholder.com/150x225?text=Inception","year":2010,"category":"Hollywood"}
    ]
    return jsonify({"trending": trending, "most_searched": most_searched})

@app.route("/search")
def search():
    q = request.args.get("q","")
    results = []
    if TMDB_KEY and q:
        try:
            resp = requests.get("https://api.themoviedb.org/3/search/movie", params={"api_key":TMDB_KEY,"query":q}).json()
            for m in resp.get("results",[])[:10]:
                poster = f"https://image.tmdb.org/t/p/w300{m.get('poster_path')}" if m.get("poster_path") else ""
                results.append({"title": m.get("title") or m.get("name"), "poster": poster, "year": (m.get('release_date') or "")[:4], "category":"Unknown"})
        except Exception as e:
            print("search error",e)
    return jsonify({"results": results})

@app.route("/find", methods=["POST"])
def find():
    body = request.get_json() or {}
    story = body.get("story","")
    lang = body.get("lang","en")
    # Use Gemini if available, otherwise return sample
    if GEMINI_KEY:
        prompt = f"""You are a movie expert. A user wrote a story fragment. Identify the most likely movie title, category (Bollywood/Hollywood/South Indian/Tollywood), short explanation (3-5 lines), year, and 5 similar movie recommendations. Provide JSON only.

Story: {story}
Language: {lang}
"""
        try:
            model = genai.GenerativeModel("gemini-1.5-mini")
            out = model.generate_content(prompt).text
            # Try to parse JSON from model; if fails, fall back
            try:
                parsed = json.loads(out)
                return jsonify(parsed)
            except:
                # fallback naive parse
                lines = out.split("\n")
                movie = lines[0] if lines else "Unknown"
                return jsonify({"movie":movie,"category":"Unknown","explanation":out,"recommendations":[],"poster":""})
        except Exception as e:
            print("gemini error", e)
            return jsonify({"movie":"Unknown","category":"Unknown","explanation":"AI error","recommendations":[],"poster":""})
    else:
        # Fallback: return a sample response
        return jsonify({
            "movie": "Inception",
            "category": "Hollywood",
            "explanation": "A thief who enters people's dreams to steal ideas is given a chance to have his past crimes forgiven if he can implant an idea into someone's mind.",
            "recommendations": ["Interstellar","Memento","Shutter Island","The Prestige","Tenet"],
            "poster": "https://via.placeholder.com/300x450?text=Inception",
            "year": 2010
        })

@app.route("/admin/add", methods=["POST"])
def admin_add():
    data = request.get_json() or {}
    pwd = data.get("password","")
    if pwd != ADMIN_PASSWORD:
        abort(401)
    item = {
        "title": data.get("title",""),
        "poster": data.get("poster",""),
        "year": data.get("year",""),
        "category": data.get("category","")
    }
    manual = load_manual()
    manual.insert(0, item)
    save_manual(manual)
    return jsonify({"ok":True, "manual_count": len(manual)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
