from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json, traceback
from pydantic import BaseModel
from openai import OpenAI

localData = {}
app = Flask(__name__, template_folder="static",  static_folder="", static_url_path="")
CORS(app)

class FilePlan(BaseModel):
    file_name: str
    func: list[str]

class FileCodeResponse(BaseModel):
    file_name: str
    code: str

class AppArchitecture(BaseModel):
    files: list[FilePlan]

client = OpenAI(base_url="https://developer.amd.com.cn/radeon/api/v1", api_key="rc-8bdb31133091973c1e23cbb5d975223b31833a777ddd0850")

@app.route("/", methods=["GET"])
def run_app():
    return render_template("web/index.html")

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

@app.route("/plan", methods=["POST"])
def plan_files():
	data = request.get_json()
	prompt = f"""
	Plan the file structure and function signatures for {data["query"]}.
	The application features a simple HTML/JS frontend and a Python backend (main.py).

	Architecture Rules:
	1. The JS frontend communicates with the Python backend exclusively using the bridge method: res = Android.callPython("func_name", JSON.stringify([param1, param2])).  // res is string
	2. The Python backend (main.py) must expose the exact functions targeted by the JS bridge.
	3. Include a simple index.html, the associated JS file, and main.py.
	4. Output the relative file paths and the list of specific function signatures or event listeners they contain.
	5. You can use any python module just import it and use it for any purpose.
	"""

	response = client.beta.chat.completions.parse(
	    model="DeepSeek-V4.1-Flash",
	    messages=[
	        {"role": "system", "content": "You are a principal software architect generating build plans for an AI app generator."},
	        {"role": "user", "content": prompt}
	    ],
	    response_format=AppArchitecture,
	    temperature=0.2
	)

	generated_plan = response.choices[0].message.parsed
	final_json_list = [file.model_dump() for file in generated_plan.files]

	print(json.dumps(final_json_list, indent=2))
	return jsonify({"plan": final_json_list})

@app.route("/processFile", methods=["POST"])
def process_file():
	data = request.get_json()
	system_prompt = """You are an automated code generator for a hybrid Android runtime.
	Each request is completely independent and stateless. You will receive:
	1. The global architecture plan (all files and functions across the app).
	2. The specific target file name you must implement right now.

	Architectural Constraints:
	- Frontend files (HTML/JS) communicate with Python exclusively via:
	    Android.callPython("function_name", [param1, param2, ...])
	- The Python entry point is 'main.py'.
	- Any function called by the JavaScript bridge must exist with matching signatures in Python.
	- Provide clean, full, working code for ONLY the requested target file without placeholders or ellipsis.
	"""
	user_prompt = f"""Target File to Generate: {data["file"]}

	App Context:
	{data["query"]}

	Complete Architecture Plan:
	{data["arch"]}

	Generate the complete, runnable source code for '{data["file"]}' according to this architecture."""

	response = client.beta.chat.completions.parse(
        model="DeepSeek-V4.1-Flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=FileCodeResponse,
        temperature=0.1
    )
	res = response.choices[0].message.parsed.code
	with open(output_path, "w", encoding="utf-8", newline="\n") as f:
	    f.write(res)
	return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

# 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