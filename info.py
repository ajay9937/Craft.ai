init_session_data = """
Your job is to act as the PROJECT ARCHITECT for a mobile application that will be generated file-by-file later.

The user will provide an application idea. Your current task is NOT to generate source code. Your task is to analyze the application idea and generate ONE complete, valid JSON project specification that another program will use to generate the application files individually.

The application runtime is a React JS Local HTML mobile frontend with access to the complete Python ecosystem. Python is executed inside the Android application runtime and JavaScript communicates with Python through the Android bridge.

TECHNICAL CONSTRAINTS (CRITICAL):

1. FRONTEND
   - Frontend uses HTML5, CSS, and React.js.
   - The application must be mobile-first and responsive.
   - React must work in the Android WebApp environment.
   - Do not assume npm or Node.js is available at runtime.
   - Do not require a Node.js server.
   - Do not require a separate backend server unless the application genuinely requires one.
   - React components must use normal React state and lifecycle mechanisms.
   - DO NOT use ES module `import` or `export` statements (no `import React from 'react'`). Use global `React.useState`, `React.useEffect`, etc.
   - ICONS MUST BE INLINE SVGS ONLY. DO NOT use the Lucide CDN script and DO NOT call `lucide.createIcons()`, as this alters the DOM outside of React and causes fatal `removeChild` errors. Hardcode the raw SVG paths directly inside the React components.
   - NEVER use manual DOM manipulation (like .innerHTML, .appendChild, or .removeChild) inside React components.
   - Ensure strictly valid HTML nesting (e.g., never put a <div> inside a <p> or <button>).
   - Mount using `ReactDOM.createRoot(document.getElementById('root')).render(<App/>)`.
   - Do not use manual DOM manipulation such as innerHTML, appendChild, removeChild, etc.
   - Use valid HTML nesting.
   - The final frontend must mount using:
     ReactDOM.createRoot(document.getElementById('root')).render(<App />)

2. JAVASCRIPT MODULE ARCHITECTURE

    The generated application runs directly inside an Android WebView/local HTML runtime.

    There is NO JavaScript bundler and NO npm build step.

    Therefore:

    - NEVER use ES module import statements.
    - NEVER use ES module export statements.
    - NEVER use require().
    - NEVER assume Node.js module resolution.
    - NEVER assume Vite, Webpack, Rollup, Parcel, or another bundler.

    All JavaScript files share the browser global runtime.

    Every file that provides a reusable symbol MUST expose that symbol through window.

    Example:

    window.ROUTES = {
        HOME: "home",
        SETTINGS: "settings"
    };

    window.useExample = function() {
        ...
    };

    window.ExampleComponent = function() {
        ...
    };

    The application entry file must consume globally exposed symbols.

    Example:

    ReactDOM.createRoot(
        document.getElementById("root")
    ).render(
        React.createElement(window.App)
    );

3. ICONS
   - Prefer inline SVG icons.
   - Do not use Lucide CDN or DOM-mutating icon libraries.
   - External icon libraries should only be used if explicitly required by the application.

4. CSS
   - The application should use the generated theme values.
   - Respect the specified colors, typography, spacing, radius, and shadows.
   - Avoid hardcoded conflicting design values unless required by a component.

5. PYTHON
   - Python is available to the application.
   - Any appropriate PyPI package may be used.
   - The Python backend should be divided into logical modules rather than placing everything in one file.
   - python/bridge.py is the boundary between JavaScript and Python.
   - Python functions exposed through the bridge must have stable names and predictable JSON-compatible inputs and outputs.

6. JAVASCRIPT → PYTHON COMMUNICATION

JavaScript calls Python using:

Android.callPython(
    "function_name",
    JSON.stringify(["param1", "param2"])
);

A recommended wrapper is:

function callPython(func, params) {
    return Android.callPython(func, JSON.stringify(params));
}

7. PYTHON → JAVASCRIPT COMMUNICATION

Python can execute JavaScript using:

app.exec("javascript_code")

Python-to-JavaScript calls must only invoke explicitly defined functions/events in the project specification.

8. API CONTRACTS

Every JavaScript-to-Python API must define:

- name
- parameters
- return
- role

Every Python-to-JavaScript execution call must define:

- name
- parameters
- role

Every JavaScript-to-Python value/query function must define:

- name
- parameters
- return
- role

9. PROJECT FILE ARCHITECTURE

The project must contain a moderate number of files.

Do NOT create a huge number of tiny files.

Do NOT put the entire application into one giant file unless the application is genuinely simple.

Each file must have a clear responsibility.

10. FILE METADATA

IMPORTANT:

The "files" object must NOT contain only:

"path": "description"

Instead every file must be represented by an object containing:

- role
- type
- depends_on
- used_by
- exports
- imports

Example:

"src/App.jsx": {
    "role": "Main application component...",
    "type": "react_component",
    "depends_on": [
        "src/hooks/useWeather.js",
        "src/components/Header.jsx"
    ],
    "used_by": [
        "src/main.jsx"
    ],
    "provides": ["window.App"],
    "requires": [
        "window.ROUTES",
        "window.useFaceDetector",
        "window.Header",
        "window.Navigation",
        "window.DetectorScreen",
        "window.HistoryScreen",
        "window.SettingsScreen"
    ]
}

PUBLIC SYMBOL CONTRACT:

    The "exports" field represents symbols that MUST be available globally at runtime.
    For JavaScript files:
    "exports": ["ROUTES"]
    means the generated file MUST define:
    window.ROUTES = ...
    For a React component:
    "exports": ["App"]
    means the generated file MUST define:
    window.App = App;
    For a hook:
    "exports": ["useFaceDetector"]
    means the generated file MUST define:
    window.useFaceDetector = useFaceDetector;
    Never expose a symbol under a different name than specified in "exports".

GLOBAL SYMBOL CONTRACT:

    Every file MUST explicitly declare:

    - "provides": symbols that this file creates and exposes to the global runtime.
    - "requires": symbols that this file reads, calls, renders, or otherwise depends on from other files.

    For JavaScript files, every item in "provides" MUST be a global window symbol.

    Examples:

    "provides": [
        "window.ROUTES",
        "window.APP_NAME"
    ]

    "requires": [
        "window.ROUTES"
    ]

    A React component:

    "provides": [
        "window.App"
    ]

    "requires": [
        "window.ROUTES",
        "window.Header",
        "window.Navigation",
        "window.DetectorScreen"
    ]

    A file with no cross-file dependencies MUST still include:

    "provides": [],
    "requires": []

    Never omit these fields.

    Every symbol in "requires" MUST be provided by exactly one file in the project.

    Every symbol in "provides" MUST be unique across the project.

    The dependency graph MUST be consistent with these symbols.

    If file A requires window.X, then the file that provides window.X MUST appear in A's depends_on list.

    If file A provides window.X and file B requires window.X, then B MUST appear in A's used_by list.

    Do not use "imports" or "exports" fields. Use only "provides" and "requires" for JavaScript cross-file symbol contracts.

    index.html MUST load frontend JavaScript files.

11. FILE TYPES

Use appropriate values for "type", such as:

- config
- html_entry
- react_entry
- react_component
- react_hook
- javascript_service
- javascript_utility
- python_entry
- python_bridge
- python_service
- python_utility
- python_config
- python_dependency_manifest
- stylesheet
- documentation
- asset_manifest

12. DEPENDENCY GRAPH

The "depends_on" field means files that must exist or whose interfaces are required before this file can be generated reliably.

The "used_by" field means files that depend on the current file.

The dependency graph must be logically consistent.

For example:

python/weather_engine.py
    depends_on:
        python/config.py
        python/analytics.py

python/bridge.py
    depends_on:
        python/weather_engine.py
        python/geo_service.py

src/services/weatherService.js
    depends_on:
        src/services/androidBridge.js

src/hooks/useWeather.js
    depends_on:
        src/services/weatherService.js

src/App.jsx
    depends_on:
        src/hooks/useWeather.js
        relevant React components

13. GENERATION ORDER

Add a top-level "generation_order" array.

This must contain the file paths in an order that respects their dependencies.

Example:

"generation_order": [
    "index.html",
    "python/requirements.txt",
    "python/config.py",
    "python/analytics.py",
    "python/weather_engine.py",
    "python/bridge.py",
    "src/utils/constants.js",
    "src/services/androidBridge.js",
    "src/services/weatherService.js",
    "src/hooks/useWeather.js",
    "src/components/Header.jsx",
    "src/App.jsx",
    "src/main.jsx"
]

A file MUST appear AFTER every dependency listed in depends_on.

There are NO exceptions.

generation_order MUST be a valid topological ordering of the dependency graph.

14. FILE GENERATION CONTEXT

Add a top-level "file_generation_rules" object.

It must explain how an individual file should be generated.

Include:

- generate_one_file_at_a_time: true
- preserve_existing_files: true
- use_dependency_context: true
- use_api_contracts: true
- do_not_generate_unlisted_files: true
- validate_api_names: true

15. PROJECT KNOWLEDGE

Add a top-level "project_contracts" object containing important shared contracts that multiple files must agree on.

Include:

- shared_data_models
- api_data_models
- global_constants
- navigation_routes
- important_runtime_assumptions

16. APP FEATURES

"app_features" must contain concrete user-visible capabilities.

Do not put implementation details in app_features.

Bad:
"Uses Python requests library"

Good:
"Displays real-time weather information"

17. OVERALL IDEA

"overall_idea" must describe:

- what the application does
- frontend architecture
- Python architecture
- Android bridge
- important data flow
- major technologies
- whether the app needs a remote server
- whether it can operate offline

18. ASSETS

The "assets" object must contain:

"relative/path/to/asset": "download URL"

Only include assets genuinely required by the application.

Do not invent URLs.

19. DEPENDENCIES

"python_packages" must contain only packages actually required by the application.

"js_cdn_packages" must contain only CDN packages genuinely required by the application.

20. UI DESIGN

Generate:

- light_theme
- colors
- typography
- spacing
- radius
- shadows

These values should form a coherent design system.

21. SCREENS

Every screen must contain:

- name
- route
- role

22. COMPONENTS

Every component must contain:

- name
- role

23. API DESIGN

Design APIs around meaningful application operations, not around individual implementation steps.

24. OUTPUT FORMAT

Return ONLY valid JSON.

Do not use Markdown.

Do not use comments.

Do not wrap the JSON in ```json.

Do not include explanations before or after the JSON.

The JSON must follow this structure:

{
  "app_features": [],
  "overall_idea": "",

  "files": {
    "relative/file/path": {
      "role": "",
      "type": "",
      "depends_on": [],
      "used_by": [],
      "exports": [],
      "imports": []
    }
  },

  "generation_order": ["file1", "file2", ...],

  "file_generation_rules": {
    "generate_one_file_at_a_time": true,
    "preserve_existing_files": true,
    "use_dependency_context": true,
    "use_api_contracts": true,
    "do_not_generate_unlisted_files": true,
    "validate_provides_requires": true,
    "validate_api_names": true,

    "cross_file_symbol_rules": {
        "use_only_declared_dependencies": true,
        "use_only_declared_provides": true,
        "global_namespace": "window",
        "never_invent_symbols": true,
        "never_use_import_export": true,
        "validate_symbol_references": true,
        "unique_provider_per_symbol": true,
        "required_symbol_must_have_provider": true
    }
},

  "project_contracts": {
    "shared_data_models": {},
    "api_data_models": {},
    "global_constants": {},
    "navigation_routes": {},
    "important_runtime_assumptions": []
  },

  "assets_to_be_downloaded": {
      "haarcascade_frontalface_default.xml":"https://raw.githubusercontent.com/opencv/opencv/refs/heads/4.x/data/haarcascades/haarcascade_frontalface_default.xml",
       "models/file1":"http://image.com"
  },

  "multi_user": false,
  "js_cdn_packages": [],
  "python_required": true,
  "python_packages": [],

  "light_theme": true,

  "colors": {},

  "typography": "",
  "spacing": "",
  "radius": "",
  "shadows": "",

  "screens": [],

  "components": [],

  "js_to_python_apis": [],

  "python_to_js_exec_calls": [],

  "js_to_python_val_func": []
}

25. THERE MUST BE A main.py FILE IN YOUR PROJECT. AND ALL THE FUNCTIONS THAT JAVASCRIPT WILL CALLTO PYTHON USING Android.CallPython the function name and parameters must be defined in main.py.

    A sample example: 

    ---- index.html:

    <html>
        <input>
        <button onclick="say()">Say</button>
        <script>
            function say(){{
                // calling python <global func_name> <param1, param2, ...>
                Android.callPython("sayHello", JSON.stringify([document.querySelector("input").value, "Hello"])); // return "OK"
            }}
            function doAlert(mes, *args){{  # multiple parameters
                alert(mes);
            }}
        </script>
    </html>

    ---- main.py:

    IS_ANDROID = False
    try:
        from web import WebApp # Android web module
        from java import jclass  # chaquopy java module
        IS_ANDROID = True
    except Exception:
        pass

    ctx = jclass("org.anvlabs.anvpy.NewActivity").ctx  // Android Context
    Toast = jclass("android.widget.Toast")

    app = None
    def sayHello(inp):
        print(f"Message from Javascript: {{inp}}")
        if IS_ANDROID:
            app.exec("doAlert('Hi from python')")  # calling JS Function non-return
            Toast.makeText(ctx, inp, Toast.LENGTH_LONG).show()  # Android toast
        return "OK"

    if IS_ANDROID:
        app = WebApp("index.html")
        app.run()
        # non stop loop on android
    else:
        pass # just pass do not start any server

IMPORTANT:

The JSON must be internally consistent.

IMPORTANT:

The JSON must be internally consistent.

Every path appearing in:
- depends_on
- used_by
- generation_order

must exist in the "files" object.

Every symbol appearing in:
- provides
- requires

must be a valid global symbol.

Every symbol in "requires" MUST have exactly one matching provider in "provides".

Every required symbol's provider MUST be listed in depends_on.

Every consumer of a provided symbol MUST be listed in used_by.

generation_order MUST place every provider before every file that requires that provider.

No symbol may have multiple providers.

No required symbol may be missing a provider.

Do not use imports or exports metadata because the runtime does not support ES modules.

API names referenced by files must exist in the API definitions.

Routes referenced by components must exist in screens.

Do not create files that are unnecessary for the application.

Do not create dependencies merely for architectural decoration.

The resulting JSON will be consumed programmatically by another application, so correctness and consistency are more important than descriptive verbosity.

The user's next message or the next chat will contain the application idea. Analyze that idea and return the complete project specification JSON according to all rules above. And make sure the output is a valid JSON Object

If you have understood what i have return only 1 else 0, no other response.
"""

tech_stack = """
	We need a multi-file html React app. That can run locally in my browser.

	TECHNICAL CONSTRAINTS (CRITICAL):
	1. Include all required CDNs inside <head>:
	   - Tailwind CSS CDN (https://cdn.tailwindcss.com)
	   - React 18 & ReactDOM 18 CDN
	   - Babel Standalone CDN (@babel/standalone)
	2. Put ALL HTML, CSS, React components, and state logic into a single <script type="text/babel"> tag.
	3. DO NOT use ES module `import` or `export` statements (no `import React from 'react'`). Use global `React.useState`, `React.useEffect`, etc.
	4. ICONS MUST BE INLINE SVGS ONLY. DO NOT use the Lucide CDN script and DO NOT call `lucide.createIcons()`, as this alters the DOM outside of React and causes fatal `removeChild` errors. Hardcode the raw SVG paths directly inside the React components.
    5. NEVER use manual DOM manipulation (like .innerHTML, .appendChild, or .removeChild) inside React components.
    6. Ensure strictly valid HTML nesting (e.g., never put a <div> inside a <p> or <button>).
	7. Mount using `ReactDOM.createRoot(document.getElementById('root')).render(<App/>)`.
	8. You can use any python module from pypi so no need to write anything from scratch you can just use any python module.

	DESIGN & UI REQUIREMENTS:
	1. Theme: Dark glassmorphism palette use less gradient colors to make it look like non-AI build.
	2. Typography & Cards: Rounded-2xl corners, subtle borders and soft drop shadows.
	3. Micro-Interactions: Hover effects on buttons.
	4. The application is a mobile application, but DO NOT render a phone mockup, device frame, bezel, notch, rounded outer container, or simulated mobile device.

	Generate the complete, production-ready files list that we need for this project. You can sub-divide the files for later debugging or to make easy modification.

	BACKEND:
	1. Use JavaScript as default backend for all the tasks.
	2. You can use any online JS Modules using CDNs for charts, face-api, 3D, etc.
	3. Use standard JS Navigator or React Module for WebCam or Microphone.
	4. Now, this is important that as you are making the index.html as main entry it must be hosted by python so a main.py file in root path is mandatory check below code on how to host a html page.

		html:

		<html>
			<input>
			<button onclick="say()">Say</button>
			<script>
				function say(){{
					// calling python <global func_name> <param1, param2, ...>
					Android.callPython("sayHello", JSON.stringify([document.querySelector("input").value, "Hello"])); // return "OK"
				}}
				function doAlert(mes, *args){{  # multiple parameters
					alert(mes);
				}}
			</script>
		</html>

		python:

		IS_ANDROID = False
		try:
			from web import WebApp # Android web module
			from java import jclass  # chaquopy java module
			IS_ANDROID = True
		except Exception:
			pass

		ctx = jclass("org.anvlabs.anvpy.NewActivity").ctx  // Android Context
		Toast = jclass("android.widget.Toast")

		app = None
		def sayHello(inp):
			print(f"Message from Javascript: {{inp}}")
			if IS_ANDROID:
				app.exec("doAlert('Hi from python')")  # calling JS Function non-return
				Toast.makeText(ctx, inp, Toast.LENGTH_LONG).show()  # Android toast
			return "OK"

		if IS_ANDROID:
			app = WebApp("index.html")
			app.run()
			# non stop loop

        Write all these functions and web module code in main.py which is present in root entry. So any function defined in main.py only is callable from JS.

		Never start any web server by yourself, if you see that it is not android environment so you cannot use web module, dont write your own server just leave. 

		Specify all the functions that javascript wants to call in main.py and remember there is no other attribute of web module except app.exec and app.run so place all python function in main.py so that javascript can call via Android.callPython

		The main.py should contain this webapp code that will host it additionaly you can add any module for your project that are availabe in python pip like for youtube download yt-dlp, or scikit-image, numpy, etc. any python module for your project.

		AND PLEASE DONT MAKE UP A MODULE YOURSELF YOU ARE FREE TO CHOOSE AND USE ANY MODULE FROM PYPI ANY API FROM WEB SO DONT test for any arbitary modules. For a feature search whole pypi python repository or in web for that python module if there please use.

		You can also use builtin chaquopy java module for accessing android classes and doing operation from here.

		But beware check if java module is available or not if not available then do all the operations except the java module android specific operation. So add a boolean variable that says if android environment or not. If not android then do not import or use the web module just leave the web module if not on android.

		Keep all these Javascript functions for bi-communication in index.html so that i can debug it. And just make sure to add try catch in python functions where javascript calls them using Android.callPython and return the response as json string which contains a key success True or False for the operation. So that it will help me for debugging later as i can get python response from the success key.

		And rememeber if you think if using python or its modules is better than using javascriot online cdn then use python.
"""

text_prompt = f"""
    The tech stack that will be used and the instructions are: {tech_stack}

    Your only Job is to return me an python array whole first item is a json containing the keys as the relative file path name for the project and the values as the usage and purpose of the files in this project and remember do not give files that can be downloadable online just give files that you can write by youself. Second element of the array conatins a python list containing all the basic features of the app according to the modern 2026 mobile apps which should be professional and "don't give features that need an external server or ai model" and you can add all the features that are provided with the app description. And the third element of array contains a complete description of js and python backend that will used to intercommunicate between them along with the modules used in python and js and all their function parameters and signatures. Use any python module in your project do not write anything from scratch.
    
    And the fourth element of array is an array that contains debugging steps like it contains Javascript functions that calls python functions for debugging like ['Android.callPython("get_info", JSON.stringify(["url"]))'].

    Remember about the testing commands see first of all i am testing these on a web app environment so give android related paramters and see if functions returns success False then i have to validate again so just provide function validation like suppose if you send in paramter a file and the function returns success False as file is not there on web app so it will always return false and i will never go forward so just test features dont test with assets, yes you can provide with full link complete no "..." at end. Ok, so provide with correct validation functions. And dont give wrong or incomplete validation func like this suppose ['Android.callPython("get_info", JSON.stringify(["http://youtube.be/......"]))']. You see this link "http://youtube.be/......" is incomplete and invlaid so either do not add this like to validation set or set a checker in python function that will return true still as the feature is used the result may not be of desired output.
    And remember the response that you give on success:false should return traceback.format_exc() not str(e) so that we can get the complete detail on line number and all.

    And the fifth element of array contains a very very short note of what kind of app whith what features u have planned just a non technical summary in short, make sure no technical word or context be there so that non programmers can easily understand what kind of app you are making.

    And the sixth element of array contains a array of python modules you have used in this project, you are free to use any python moudle for any above features i insist please use any python module and don't rely much on javascript cdn module if they are not available and dont make up your own moudle use from pypi.

    And the seventh element contains a object whose key is the relative file location and value is the online url, so before running the app what all assets i need that i can download and save beforehand project execution. So in the first array where you give files do not put these downloadable files in the first element of array put all of those assets and their online url here.

    And rememeber the array that u make does not have any comments so that it is JSON parsable.

    THIS IS A LINK THAT CONATINS SOME SAMPLES FOR EXTRA-ORDINARY FEATURES CHECK IT OUT: https://drive.google.com/uc?export=download&id=1BwE_drUfNUEZ4M1O8apY_C7xE16V5Z0j
"""

JS_FRONTEND_VALIDATION = """
    PHNjcmlwdD4NCiAgICBmdW5jdGlvbiBsb2dFcnJvclRvU2VydmVyKGRhdGEpIHsNCiAgICAgICAgd2luZG93LnBhcmVudC50ZXN0ZXJFcnJvcihkYXRhKTsNCiAgICB9DQoNCg0KICAgIC8vIDEuIFVuaWZpZWQgTGlzdGVuZXIgZm9yIFJ1bnRpbWUgQU5EIFJlc291cmNlIEVycm9ycw0KICAgIHdpbmRvdy5hZGRFdmVudExpc3RlbmVyKCdlcnJvcicsIGZ1bmN0aW9uKGV2ZW50KSB7DQogICAgICAgIC8vIENoZWNrIGlmIHRoZSBlcnJvciB0YXJnZXQgaXMgYW4gSFRNTCBlbGVtZW50IChtZWFuaW5nIGEgcmVzb3VyY2UgZmFpbGVkIHRvIGxvYWQpDQogICAgICAgIGlmIChldmVudC50YXJnZXQgJiYgKGV2ZW50LnRhcmdldC50YWdOYW1lID09PSAnU0NSSVBUJyB8fCBldmVudC50YXJnZXQudGFnTmFtZSA9PT0gJ0xJTksnIHx8IGV2ZW50LnRhcmdldC50YWdOYW1lID09PSAnSU1HJykpIHsNCiAgICAgICAgICAgIGxvZ0Vycm9yVG9TZXJ2ZXIoew0KICAgICAgICAgICAgICAgIHR5cGU6ICdSZXNvdXJjZSBMb2FkIEVycm9yJywNCiAgICAgICAgICAgICAgICBtZXNzYWdlOiBgRmFpbGVkIHRvIGxvYWQ6ICR7ZXZlbnQudGFyZ2V0LnNyYyB8fCBldmVudC50YXJnZXQuaHJlZn1gLA0KICAgICAgICAgICAgICAgIHNjcmlwdFNyYzogZXZlbnQudGFyZ2V0LnNyYyB8fCBldmVudC50YXJnZXQuaHJlZiwNCiAgICAgICAgICAgICAgICBodG1sRWxlbWVudDogZXZlbnQudGFyZ2V0Lm91dGVySFRNTA0KICAgICAgICAgICAgfSk7DQogICAgICAgIH0gZWxzZSB7DQogICAgICAgICAgICAvLyBPdGhlcndpc2UsIGl0J3MgYSBzdGFuZGFyZCBKYXZhU2NyaXB0IFJ1bnRpbWUgRXJyb3INCiAgICAgICAgICAgIGxvZ0Vycm9yVG9TZXJ2ZXIoew0KICAgICAgICAgICAgICAgIHR5cGU6ICdSdW50aW1lIEVycm9yJywNCiAgICAgICAgICAgICAgICBtZXNzYWdlOiBldmVudC5tZXNzYWdlLA0KICAgICAgICAgICAgICAgIHNjcmlwdFNyYzogZXZlbnQuZmlsZW5hbWUgfHwgJ0lubGluZSBTY3JpcHQnLA0KICAgICAgICAgICAgICAgIGxpbmU6IGV2ZW50LmxpbmVubywNCiAgICAgICAgICAgICAgICBjb2x1bW46IGV2ZW50LmNvbG5vLA0KICAgICAgICAgICAgICAgIHN0YWNrOiBldmVudC5lcnJvciA/IGV2ZW50LmVycm9yLnN0YWNrIDogbnVsbA0KICAgICAgICAgICAgfSk7DQogICAgICAgIH0NCiAgICB9LCB0cnVlKTsNCg0KICAgIC8vIDIuIENhdGNoIHVuaGFuZGxlZCBQcm9taXNlIHJlamVjdGlvbnMNCiAgICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcigndW5oYW5kbGVkcmVqZWN0aW9uJywgZnVuY3Rpb24oZXZlbnQpIHsNCiAgICAgICAgbG9nRXJyb3JUb1NlcnZlcih7DQogICAgICAgICAgICB0eXBlOiAnVW5oYW5kbGVkIFByb21pc2UgUmVqZWN0aW9uJywNCiAgICAgICAgICAgIG1lc3NhZ2U6IGV2ZW50LnJlYXNvbiA/IChldmVudC5yZWFzb24ubWVzc2FnZSB8fCBldmVudC5yZWFzb24udG9TdHJpbmcoKSkgOiAiVW5rbm93biBSZWFzb24iLA0KICAgICAgICAgICAgc3RhY2s6IGV2ZW50LnJlYXNvbiAmJiBldmVudC5yZWFzb24uc3RhY2sgPyBldmVudC5yZWFzb24uc3RhY2sgOiBudWxsDQogICAgICAgIH0pOw0KICAgIH0pOw0KDQogICAgLy8gMy4gQ2F0Y2ggQmFiZWwncyBpbnRlcm5hbCBTeW50YXggRXJyb3JzDQogICAgLy8gQmFiZWwgb2Z0ZW4gbG9ncyBjb21waWxhdGlvbiBlcnJvcnMgZGlyZWN0bHkgdG8gdGhlIGNvbnNvbGUgaW5zdGVhZCBvZiB0aHJvd2luZyB0aGVtIGdsb2JhbGx5DQogICAgY29uc3Qgb3JpZ2luYWxDb25zb2xlRXJyb3IgPSBjb25zb2xlLmVycm9yOw0KICAgIGNvbnNvbGUuZXJyb3IgPSBmdW5jdGlvbiguLi5hcmdzKSB7DQogICAgICAgIGNvbnN0IGVycm9yU3RyaW5nID0gYXJncy5qb2luKCcgJyk7DQogICAgICAgIA0KICAgICAgICBpZiAoZXJyb3JTdHJpbmcuaW5jbHVkZXMoJ0lubGluZSBCYWJlbCBzY3JpcHQ6JykgfHwgZXJyb3JTdHJpbmcuaW5jbHVkZXMoJ1N5bnRheEVycm9yJykpIHsNCiAgICAgICAgICAgIGxvZ0Vycm9yVG9TZXJ2ZXIoew0KICAgICAgICAgICAgICAgIHR5cGU6ICdCYWJlbCBDb21waWxhdGlvbiBFcnJvcicsDQogICAgICAgICAgICAgICAgbWVzc2FnZTogZXJyb3JTdHJpbmcsDQogICAgICAgICAgICAgICAgc2NyaXB0U3JjOiAnSW5saW5lIEJhYmVsIFNjcmlwdCcsDQogICAgICAgICAgICAgICAgLy8gRXh0cmFjdCBsaW5lIG51bWJlciBmcm9tIEJhYmVsJ3MgZm9ybWF0IGUuZy4sICg3Njo4KQ0KICAgICAgICAgICAgICAgIGxpbmU6IGVycm9yU3RyaW5nLm1hdGNoKC9cKChcZCspOihcZCspXCkvKSA/IGVycm9yU3RyaW5nLm1hdGNoKC9cKChcZCspOihcZCspXCkvKVsxXSA6IDANCiAgICAgICAgICAgIH0pOw0KICAgICAgICB9DQogICAgICAgIA0KICAgICAgICBvcmlnaW5hbENvbnNvbGVFcnJvci5hcHBseShjb25zb2xlLCBhcmdzKTsNCiAgICB9Ow0KPC9zY3JpcHQ+
"""

