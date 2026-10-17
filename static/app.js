function $(val){
	return document.querySelector(val);
}

var processingBox, queryBox, promptBox, loaderText, testerWindow, navBar, phoneMock;
var debugBtn;
var showUI = false, chatIndex = 0;
var mainSID, fileSID, testerFunc = [], output, jsError = [];
const MAX_VALIDATION = 10, QUERY_MODEL = "gemini-3.1-flash-lite", GENERATIVE_MODEL = "gemini-3.5-flash", MODIFICATION_MODEL = "gemini-3.5-flash", PLANNER_MODEL = "gemini-3.6-flash";

class Android{
	static callPython(name, args){
		let formData = new FormData();
		formData.append("func", name);
		formData.append("args", args);

		let xhr = new XMLHttpRequest();
		xhr.open("POST", "/func", false);
		xhr.send(formData);

		if(xhr.readyState == 4){
			if(xhr.status == 200){
				let obj = JSON.parse(xhr.responseText);
				if(obj["success"]){
					return obj["data"];
				}
				else{
					window.console.error(obj["data"]);
					return "{}";
				}
			}
			else{
				window.console.error("No connection");
				return null;
			}
		}
		else{
			window.console.error("No connection");
			return null;
		}
	} 
}

function reloadTester() {
    return new Promise((resolve) => {
        testerWindow.onload = async () => {
            testerWindow.contentWindow.Android = Android;

            // Give React/Babel/useEffect/API calls time to execute
            await new Promise(resolve => setTimeout(resolve, 2000));

            resolve();
        };

        testerWindow.src = "/static/output/index.html?t=" + Date.now();
    });
}

function setPrcMessage(mes){
	$(".chats").children[chatIndex].children[0].children[1].innerHTML = mes;
}

function createChatQuery(){
	let box = document.createElement("div");
	box.innerHTML = $(".tmp").innerHTML;
	box.setAttribute("class", "ai");
	$(".chats").appendChild(box);
	chatIndex = $(".chats").childElementCount - 1;
}

function showAgentOutput(mes){
	let box = $(".chats").children[chatIndex];
	box.style.background = "lavender";
	box.children[0].style.display = "none";
	box.children[1].style.display = "block";
	box.children[1].innerHTML = mes;
}

function callPython(name, args){
	let formData = new FormData();
	formData.append("func", name);
	formData.append("args", args);

	let xhr = new XMLHttpRequest();
	xhr.open("POST", "/func", false);
	xhr.send(formData);

	if(xhr.readyState == 4){
		if(xhr.status == 200){
			let obj = JSON.parse(xhr.responseText);
			if(obj["success"]){
				return {success: true, data: obj["data"]};
			}
			else{
				return {success: false, data: obj["data"]};
			}
		}
		else{
			window.console.error("No connection");
			return {};
		}
	}
	else{
		window.console.error("No connection");
		return {};
	}
}

function setTesterWindow(){
	let xhr = new XMLHttpRequest();
	xhr.open("GET", "/set_tester", false);
	xhr.send();

	if(xhr.readyState == 4 && xhr.status == 200){
		let obj = JSON.parse(xhr.responseText);
		if(obj["success"]){
			testerWindow.src = "/../output/index.html";
		}
		else{
			return obj["data"];
		}
	}
	else{
		return null;
	}
	return "";
}

async function updateMain(){
	let k = 0;
	while(k < MAX_VALIDATION){
		response = await fetch("/set_tester");
		let data = await response.json();
		console.log(`validation: #${k}:`,data);
		if(data["success"]){
			console.log("main.py entry level ok");
			break;
		}
		else{
			console.log("updating main.py entry level");
			await updateFile(data["data"] + " \nCarefully look for all the code all other errors that can happen and fix that be precise test and validate yourself.", 1);
		}
		k++;
	}
}

async function updateFile(query, mode){
	var arr = Object.keys(output[0]);
	if(mode != 0){
		if(mode == 1) arr = arr.filter(elem => elem.split(".").at(-1) == "py");
		else arr = arr.filter(elem => elem.split(".").at(-1) != "py");
	}
	try {
		const response = await fetch("/ask_query", {
		    method: "POST",
		    headers: {
		        "Content-Type": "application/json"
		    },
		    body: JSON.stringify({
		        id: fileSID,
		        input: query,
		        model: QUERY_MODEL,
		        files: arr
		    })
		});
		const data = await response.json();
		if(data["success"]){
			console.log("files to be modified after validation:", data["output"]);
			let response = await fetch("/update_files", {
		        method: "POST",
		        headers: {
		            "Content-Type": "application/json"
		        },
		        body: JSON.stringify({
		            id: fileSID,
		            input: query,
		            model: MODIFICATION_MODEL,
		            files: JSON.parse(data.output)
		        })
		    });

		    let updateData = await response.json();

		    if (updateData.success) {
		        console.log("files updated");
		        console.log("downloads needed:", data["downloadss"])
		        //fileSID = updateData.id;
		        await updateMain();
		    } else {
		        console.error(updateData.error);
		    }
		}
		else{
			console.error(data["error"]);
		}
	}
	catch (e){
		console.error(e);
	}
}

async function validateFunc(){
	let err = {};
	console.log("BACKEND FILES VALIDATION");
	for(let i = 0; i < testerFunc.length; i++){
		let res = eval(testerFunc[i].replace("Android.callPython", "callPython"));
		let vld = false
		if(res["success"]){
			let obj = JSON.parse(res["data"]);
			if (Object.hasOwn(obj, "success")) {
				vld = obj["success"];
			}
			else{
				vld = true
			}
		}
		else{
			vld = false
		}
		if(vld){
			console.log("validated, repsonse:", JSON.stringify(res["data"]));
		}
		else{
			err[testerFunc[i]] = res["data"];
			//await updateFile(testerFunc[i] + " error: " + JSON.stringify(res["data"]), 1);
		}
	}
	if(Object.keys(err).length > 0){
		console.log("ASKING VALIDATION:", Object.keys(err).join());
		await updateFile(JSON.stringify(err), 1);
		await fetch("/set_tester");
		return false;
	}
	return true;
}

async function loadFiles(data){
	try{
		data = JSON.parse(data);
		if(data["success"]){
			//fileSID = data["id"];
			processingBox.style.opacity = "0";
			processingBox.style.top = "50px";
			showAgentOutput("Files generated");
			console.log("Files generated");
			//load_session();
		}
		else{
			console.log("error:", data["error"]);
		}
	}
	catch{
		console.log(data);
	}
}

async function processSession(data){
	if(data["success"]){
		mainSID = data["id"];
		output = JSON.parse(data["output"].replace("```json", "").replace("```python", "").replace("```", ""));
		console.log(output);
		//testerFunc = output[3];
		console.log("Session id:", mainSID);
		showAgentOutput(output["overall_idea"]);
		createChatQuery();
		setPrcMessage("Generating files accordingly");
		console.log("Requesting files...");
		await fetch("/generate", {
		    method: "POST",
		    headers: {
		        "Content-Type": "application/json"
		    },
		    body: JSON.stringify({
		        id: mainSID,
		        model: GENERATIVE_MODEL,
		        files: output["files"],
		        order: output["generation_order"]
		    })
		})
		.then(response => response.text())
		.then(data => loadFiles(data));
	}
	else{
		console.error("Plan generation error:", data["error"])
	}
}

async function submitQuery(){
	let box = document.createElement("div");
	box.innerHTML = queryBox.value;
	$(".chats").appendChild(box);

	createChatQuery();

	/*setTimeout(() => {
		setTimeout(() => {
			box.style.background = "lavender";
			box.children[0].style.display = "none";
			box.children[0].children[1].innerHTML = "Files generated";
			box.children[1].style.display = "block";
		}, 2000);
	}, 2000);*/
	if(fileSID == undefined){
		console.log("Creating session");
		setPrcMessage("Processing your query and making plans");
		fetch("/create_session", {
		    method: "POST",
		    headers: {
		        "Content-Type": "application/json"
		    },
		    body: JSON.stringify({
		        input: queryBox.value,
		        model: PLANNER_MODEL
		    })
		})
		.then(response => response.json())
		.then(data => processSession(data));
	}
	else{
		setPrcMessage("Processing your query and modifying.");
		await updateFile(queryBox.value, 0);
		await load_session();
	}
}

async function load_session(){
	createChatQuery();
	setPrcMessage("Assembling data and formats");
	fetch("/load_session", {
	    method: "POST",
	    headers: {
	        "Content-Type": "application/json"
	    },
	    body: JSON.stringify({
	       
	    })
	})
	.then(response => response.json())
	.then(async data => {
		output = JSON.parse(data[1]);
		testerFunc = output[3];
		fileSID = data[0];
		let num = 0;
		setPrcMessage("Validating entry files");
		await updateMain();
		while (num < MAX_VALIDATION) {
		    try {
		    	setPrcMessage("source validation #" + (num + 1));
		        console.log("Validation #" + (num + 1));
		        if (await validateFunc()) {
		            break;
		        }

		        num++;
		    } catch (e) {
		        console.error(e);
		        break;
		    }
		}
		console.log("Backend Validation succeded");
		setPrcMessage("Backend Validation succeded");
		jsError = [];
		await reloadTester();
		testerWindow.contentWindow.Android = Android;
		if(jsError.length > 0){
			k = 0;
			while(k < MAX_VALIDATION){
				if(jsError.length == 0){
					break;
				}
				setPrcMessage("UI validation #" + (k + 1));
				console.log("Frontend files in update");
				await updateFile(JSON.stringify(jsError) + " \nThe above JSON Array contains a list of JSON Objects that contains error on the React or HTML. They keys of the objects are error Type, error Message, error file location, error line, error column, error stack", 2);
				jsError = [];
				await reloadTester();
				console.log("Error:", jsError);
				k++;
			}
		}
		else{
			console.log("Frontend Validation succeded");
			showAgentOutput("Done.")
		}
	});
}

function testerError(data){
	jsError.push(data);
}

function triggerUI(){
	if(showUI){
		navBar.style = "";
		phoneMock.style = "";
		debugBtn.style = "";
	}
	else{
		navBar.style = "pointer-events: none; transform: translate3d(-30vw, 0, 0)";
		phoneMock.style = "opacity:1; pointer-events:auto";
		debugBtn.style = "background:#b3b3ff";
	}
	showUI = !showUI;
}

function onStart(){
	processingBox = $(".processing-text");
	queryBox = $(".query-box");
	promptBox = $(".prompt-box");
	loaderText = $(".loader-text");
	navBar = $(".nav_bar");
	phoneMock = $(".tester");
	testerWindow = $("iframe");
	debugBtn = $(".debug-button");
	testerWindow.onload = () => {
	    testerWindow.contentWindow.Android = Android;
	};
	processingBox.style.top = processingBox.offsetHeight + "px";
	fetch("/reset_session").
	then(response => response.json()).
	then(data => {
		console.log(data);
	});
	//load_session();
}    