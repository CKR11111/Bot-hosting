import os
import subprocess
import zipfile
import shutil
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Bot haru store hune directory
BASE_DIR = "all_bots"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Running processes track garna
procs = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files.get('file')
        bot_id = request.form.get('bot_id', 'bot1') # Default bot1 yedi ayena bhane
        
        if not file:
            return jsonify({"error": "No file uploaded"}), 400
        
        bot_path = os.path.join(BASE_DIR, bot_id)
        
        # Purano bot folder chha bhane delete garne
        if os.path.exists(bot_path):
            shutil.rmtree(bot_path)
        
        os.makedirs(bot_path)

        # Zip file save garne
        zip_path = os.path.join(bot_path, "bot.zip")
        file.save(zip_path)

        # Extract garne
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(bot_path)
            
        return jsonify({"msg": "Bot Deployed Successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/start/<bot_id>')
def start(bot_id):
    try:
        # Check if bot exists
        bot_path = os.path.join(BASE_DIR, bot_id)
        main_py = os.path.join(bot_path, "main.py")
        
        if os.path.exists(main_py):
            # Yedi tyo bot pahile dekhi chalirakheko chha bhane stop garne
            if bot_id in procs:
                procs[bot_id].terminate()
            
            # Naya process start garne
            p = subprocess.Popen(
                ['python3', main_py], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                cwd=bot_path # Bot ko folder bhitrai basera run garna
            )
            procs[bot_id] = p
            return jsonify({"msg": f"Bot {bot_id} is now ONLINE!"})
        else:
            return jsonify({"error": "main.py not found in the uploaded zip!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Hosting platform ko PORT prioritize garne
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
