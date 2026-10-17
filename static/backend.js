var processingBox, queryBox, promptBox, loaderText, testerWindow, navBar, phoneMock;
var debugBtn;
var showUI = false, chatIndex = 0;

function $(val){
	return document.querySelector(val);
}

class Android{
	static callPython(name, args){
		let formData = new FormData();
		formData.append("func", name);
		formData.append("args", JSON.stringify(args));

		let xhr = new XMLHttpRequest();
		xhr.open("POST", "/func", false);
		xhr.send(formData);

		if(xhr.readyState == 4){
			if(xhr.status == 200){
				let obj = JSON.parse(xhr.responseText);
				if(obj["success"]){
					return JSON.stringify(obj["data"]);
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
	setTesterWindow()
}    

async function processFiles(query, data){
	console.log("processing files")
	for(let i = 0; i < data.length; i++){
		const response = await fetch("/processFile", {
		    method: "POST",
		    headers: {
		        "Content-Type": "application/json"
		    },
		    body: JSON.stringify({
		        query: query,
		        arch: JSON.stringify(data),
		        file: data[i]["file_name"]
		    })
		});

		if (!response.ok) {
		    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
		}

		const res = await response.json();

		if (!res.success) {
		    console.error("Processing failed:", res);
		}
		else{
			console.log(`${data[i]["file_name"]} done`)
		}
	}
}
// processFiles("i need a youtube video downloader app.", [
//   {
//     "file_name": "index.html",
//     "func": [
//       "function onDownloadClick()",
//       "function onFetchInfoClick()",
//       "function updateStatus(message)",
//       "function updateVideoInfo(info)",
//       "function onBridgeReady()"
//     ]
//   },
//   {
//     "file_name": "app.js",
//     "func": [
//       "function callPython(funcName, params)",
//       "function fetchVideoInfo()",
//       "function downloadVideo()",
//       "function handlePythonResponse(response)",
//       "function showError(error)",
//       "function showSuccess(message)"
//     ]
//   },
//   {
//     "file_name": "main.py",
//     "func": [
//       "def get_video_info(url: str) -> dict",
//       "def download_video(url: str, format_id: str, output_path: str) -> dict",
//       "def get_available_formats(url: str) -> list",
//       "def get_download_progress() -> dict",
//       "def cancel_download() -> dict",
//       "def get_default_download_path() -> str",
//       "def check_yt_dlp_installed() -> bool",
//       "def install_yt_dlp() -> dict"
//     ]
//   }
// ])

async function submitQuery(){
	console.log("asking request")
	let box = document.createElement("div");
	box.innerHTML = queryBox.value;
	$(".chats").appendChild(box);

	fetch("/plan", {
		method: "POST",
	    headers: {
	        "Content-Type": "application/json"
	    },
	    body: JSON.stringify({
	        query: queryBox.value
	    })
	})
	.then(response => response.json())
	.then(data => processFiles(data)["plan"]);
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

function setTesterWindow(){
	let xhr = new XMLHttpRequest();
	xhr.open("GET", "/set_tester", false);
	xhr.send();

	if(xhr.readyState == 4 && xhr.status == 200){
		let obj = JSON.parse(xhr.responseText);
		console.log(obj)
		if(obj["success"]){
			testerWindow.src = "static/output/index.html";
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
