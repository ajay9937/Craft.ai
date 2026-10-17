import os
import sys
import json
import time
import base64
import mimetypes
import traceback
import uuid
from pathlib import Path
from info import init_session_data, text_prompt, JS_FRONTEND_VALIDATION
from werkzeug.utils import secure_filename
from schema import session_schema, generative_schema, update_schema
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__, template_folder="static",  static_folder="", static_url_path="")
localData = {}
CORS(app)

# Replace with your actual OpenAI API key or set it in your environment variables
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY"))

sys.path.append("./static/output")
MAX_TPM = 240000
current_tpm_usage = 0
build_data = {}
sessions_db = {}  # To track OpenAI chat history

class MockUsage:
    def __init__(self, total_tokens):
        self.total_tokens = total_tokens

class MockResponse:
    def __init__(self, output_text, session_id, total_tokens):
        self.output_text = output_text
        self.id = session_id
        self.usage = MockUsage(total_tokens)

def chat_with_openai(model, input_data, previous_interaction_id=None, system_instruction=None, response_format=None):
    # Automatically map legacy gemini model names to standard OpenAI ones
    if "gemini" in model.lower():
        model = "gpt-4o"
        
    messages = []
    if previous_interaction_id and previous_interaction_id in sessions_db:
        messages = sessions_db[previous_interaction_id].copy()
    else:
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

    user_text = ""
    if isinstance(input_data, str):
        user_text = input_data
    elif isinstance(input_data, list):
        for item in input_data:
            if isinstance(item, dict) and item.get("type") == "text":
                user_text += item.get("text", "") + "\n"
                
    messages.append({"role": "user", "content": user_text})
    
    kwargs = {
        "model": model,
        "messages": messages
    }
    
    if response_format:
        if response_format.get("type") == "number":
            messages[-1]["content"] += "\nPlease return ONLY a valid number."
        elif response_format.get("mime_type") == "application/json" or response_format.get("type") == "json_object":
            messages[-1]["content"] += "\nPlease return ONLY valid JSON. Do not include markdown formatting like ```json."
            if "schema" in response_format:
                messages[-1]["content"] += f"\nConform exactly to this JSON schema: {json.dumps(response_format['schema'])}"
    
    response = client.chat.completions.create(**kwargs)
    out_text = response.choices[0].message.content.strip()
    tokens = response.usage.total_tokens
    
    # Strip markdown block formatting if present
    if out_text.startswith("```json"):
        out_text = out_text[7:]
    elif out_text.startswith("```"):
        out_text = out_text[3:]
    if out_text.endswith("```"):
        out_text = out_text[:-3]
    out_text = out_text.strip()
    
    # Save back to sessions history
    session_id = previous_interaction_id if previous_interaction_id else str(uuid.uuid4())
    messages.append({"role": "assistant", "content": out_text})
    sessions_db[session_id] = messages
    
    return MockResponse(out_text, session_id, tokens)

def get_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type:
        return mime_type

    suffix = Path(file_path).suffix.lower()

    custom_types = {
        ".jsx": "text/javascript",
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".ts": "text/typescript",
        ".tsx": "text/typescript",
        ".py": "text/x-python",
        ".css": "text/css",
        ".html": "text/html",
        ".htm": "text/html",
        ".json": "application/json",
        ".xml": "application/xml",
        ".txt": "text/plain",
        ".md": "text/markdown",
    }

    return custom_types.get(suffix, "text/plain")

def check_limit(model):
    global current_tpm_usage
    
    if "gemini" in model.lower():
        model = "gpt-4o"
        
    if not os.path.exists("limits.json"):
        with open("limits.json", "w") as f:
            f.write(json.dumps({}))
            
    limits = json.loads(open("limits.json").read())
    
    if model not in limits:
        limits[model] = [0, 0]
        
    f = open("limits.json", "w")
    if limits[model][0] == 0:
        limits[model][0] = time.time()
    else:
        t = time.time() - limits[model][0]
        if t < 15 and t > 0:
            print(f"Approaching RPM limit. Sleeping for {(15 - t)} seconds...")
            time.sleep(15 - t)
        limits[model][0] = time.time()
    print("tpm usage:", current_tpm_usage)
    if limits[model][1] == 0:
        limits[model][1] = time.time()
    else:
        t = time.time() - limits[model][1]
        if t >= 60:
            current_tpm_usage = 0
            limits[model][1] = time.time()
        elif current_tpm_usage > (MAX_TPM - 5000):
            sleep_time = 60 - (time.time() - limits[model][1])
            if sleep_time > 0:
                print(f"Approaching TPM limit. Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)
            current_tpm_usage = 0
            limits[model][1] = time.time()
    f.write(json.dumps(limits))
    f.close()

@app.route("/", methods=["GET"])
def run_app():
    return render_template("web/index.html")

@app.route("/tester", methods=["GET"])
def run_tester():
    return send_from_directory("static/output", "index.html")

@app.route("/set_tester", methods=["GET"])
def exec_tester():
    global localData
    try:
        exec(open("./static/output/main.py").read(), localData)
        return jsonify({
            "success": True
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "data": str(e)
        })

@app.route("/reset_session", methods=["GET"])
def reset_session():
    global build_data
    with open("data.json", "r") as f:
        build_data = json.loads(f.read())
    if build_data.get("session_id", "") == "":
        try:
            check_limit("gpt-4o")
            session = chat_with_openai(
                model="gpt-4o",
                input_data=init_session_data,
                response_format={
                    "type": "number"
                }
            )
            build_data["session_id"] = session.id
            f = open("data.json", "w")
            f.write(json.dumps(build_data))
            f.close()
        except Exception as e:
            return jsonify({
                    "success": False,
                    "error": str(e)
                })
    return jsonify({
            "success": True,
            "session_id": build_data["session_id"]
        })

@app.route("/func", methods=["POST"])
def run_func():
    global localData
    try:
        func = request.form["func"]
        params = json.loads(request.form["args"])
        if func in localData:
            res = localData[func](*params)
            return jsonify({
                "success": True,
                "data": res,
            })
        else:
            return jsonify({
                "success": False,
                "data": f"{func} not found: "
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "data": traceback.format_exc()
        })

@app.route("/load_session", methods=["GET", "POST"])
def load_session():
    return open("info.txt").read()

@app.route("/ask_query", methods=["POST"])
def ask_query():
    global current_tpm_usage
    data = request.get_json()
    prompt = f"""
    I have a query: {data["input"]} and the files are: {data["files"]}, so tell me which files among these files i need to change the code to solve the query, so just give me a JSON array containing the file names that needs to be changed, no other explanation or output just a JSON array.
    """
    try:
        check_limit(data["model"])
        session = chat_with_openai(
            model=data["model"],
            input_data=prompt,
            system_instruction="You are an expert React and Python developer. Carefully inspect the error and list the files affected.",
            previous_interaction_id=data["id"],
            response_format={
                "type": "text",
                "mime_type": "application/json",
            }
        )
        tokens_used = session.usage.total_tokens
        current_tpm_usage += tokens_used
        out = session.output_text.replace("```json", "").replace("```python", "").replace("```", "")
        return jsonify({
            "success": True,
            "output": out
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/update_files", methods=["POST"])
def update_files():
    global current_tpm_usage
    data = request.get_json()
    tmp_id = data["id"]
    try:
        for i in data["files"]:
            file_path = f"./static/output/{i}"
            
            # 1. READ FILE FIRST
            with open(file_path, "r") as f:
                lines = f.readlines()
                
            # 2. INJECT LINE NUMBERS FOR THE LLM
            numbered_code = ""
            for idx, line in enumerate(lines):
                numbered_code += f"{idx}: {line}"
            
            # 3. UPDATE PROMPT WITH THE NUMBERED CODE
            prompt = f"""
            I have a query: {data["input"]} 
            I am working on the file: {i}.
            
            Here is the current file content with exact line numbers:
            ```python
            {numbered_code}
            ```
            
            Modify the file according to the query. Give me an array whose first element is an array of arrays in the format [start_line_index, end_line_index, "replacement_text"].
            - Use the EXACT line numbers provided in the code block above.
            - start_line_index (inclusive) to end_line_index (exclusive).
            - To insert text without deleting, make start_line_index and end_line_index the same.
            - Only replace the lines that need to be changed. DO NOT delete code unless explicitly asked.
            - Provide EXACTLY valid JSON, no markdown formatting or extra text.

            and the second element of array contains a json object while represent files that you want me to download like file relative path as key and the downloadable url as value
            """
            
            check_limit(data["model"])
            session = chat_with_openai(
                model=data["model"],
                input_data=[
                    {"type": "text", "text": prompt}
                ],
                previous_interaction_id=tmp_id,
                system_instruction="You are an expert React and Python developer. Fix the particular bug completely, look for indentations in python files and validate all.",
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": update_schema
                }
            )
            tokens_used = session.usage.total_tokens
            current_tpm_usage += tokens_used
            edits = json.loads(session.output_text)[0]
            
            # Reverse sort prevents index shifting
            edits.sort(key=lambda x: x[0], reverse=True)
            
            # 4. APPLY EDITS
            for start, end, text in edits:
                if text == "":
                    lines = lines[:start] + lines[end:]
                else:
                    if not text.endswith('\n'):
                        text += '\n'
                    lines = lines[:start] + [text] + lines[end:]
                
            with open(file_path, "w") as f:
                f.writelines(lines)

        return jsonify({
            "success": True,
            "id": tmp_id,
            "downloads": json.loads(session.output_text)[1]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": traceback.format_exc()
        })

@app.route("/create_session", methods=["POST"])
def make_session():
    global current_tpm_usage, build_data
    data = request.get_json()
    try:
        check_limit(data["model"])
        session = chat_with_openai(
            model=data["model"],
            input_data=data["input"],
            previous_interaction_id=build_data.get("session_id"),
            system_instruction="You are an expert React and Python developer.",
            response_format={
                "type": "text",
                "mime_type": "application/json"
            }
        )
        tokens_used = session.usage.total_tokens
        current_tpm_usage += tokens_used
        out = session.output_text.replace("```json", "").replace("```python", "").replace("```", "")
        f = open("info.txt", "w")
        f.write(json.dumps([session.id, out], indent=4))
        f.close()
        return jsonify({
            "success": True,
            "id": session.id,
            "output": session.output_text
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/generate", methods=["POST"])
def generate_files():
    global current_tpm_usage
    data = request.get_json()
    files = data["files"]
    order = data["order"]
    try:
        for file in order:
            arr = []
            inp = []
            for i in files[file]["depends_on"]:
                arr.append(files[i])
                file_path = "static/output/" + i
                if os.path.exists(file_path):
                    print(f"Adding file {i} for prompt injection.")
                    with open(file_path, "r", encoding="utf-8") as f_in:
                        file_content = f_in.read()
                    # Feed the file as raw text directly into the chat prompt
                    inp.append({"type": "text", "text": f"\n--- Content of {i} ---\n{file_content}\n--- End of {i} ---\n"})

            main_script = f"""
                Now you need to generate the contents of each files according to the json data we have discussed in previous chat, carefully inspect the js and python methods. Also check the file generation order we have discussed.

                Before generating a file:

                1. Read the file's depends_on list.
                2. Read the exports of every dependency.
                3. Determine the exact global symbols provided by those dependencies.
                4. Only reference those symbols.
                5. Do not invent variables, functions, hooks, components, routes, API names, or constants.
                6. If a required symbol does not exist in the dependency graph, the specification is invalid and must be corrected before file generation.

                These are the list of all files that we are processing in this order: {",".join(order)}.
                Current file for processing is: {file}. And we have discussed this following information about the file: {json.dumps(files[file])}.
                And here is the data of the dependents tht conatins their roles and the global states they provide:  {json.dumps(arr)}

                Generate code for {file} and return only the text content of this no ''' in start or end.
            """
            inp.insert(0, {"type": "text", "text": main_script})
            print("========== OPENAI INPUT ==========")

            for item in inp:
                print(item)

            print("==================================")
            print(f"Processing {file}")
            
            response = chat_with_openai(
                model=data["model"],
                previous_interaction_id=data["id"],
                system_instruction="You are an expert React and Python developer. Write no bug and best quality professional code.",
                input_data=inp
            )

            tokens_used = response.usage.total_tokens
            current_tpm_usage += tokens_used
                
            file_path = Path("static/output/" + file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch(exist_ok=True)
            
            output = response.output_text
            
            if file_path.suffix == ".js":
                output = output.replace("```javascript", "").replace("```", "")
            elif file_path.suffix == ".css":
                output = output.replace("```css", "").replace("```", "")
            elif file_path.suffix == ".py":
                output = output.replace("```python", "").replace("```", "")
            elif file_path.suffix == ".html":
                output = output.replace("```html", "").replace("```", "")
                
            if file == "index.html":
                output = base64.b64decode(JS_FRONTEND_VALIDATION).decode('utf-8') + output
                
            print("./static/output/" + file)
            
            with open("./static/output/" + file, "w") as f:
                f.write(output)
            print("sleeping for 60 seconds")
            time.sleep(60)
                
        return jsonify({
            "success": True
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": traceback.format_exc()
        })

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)