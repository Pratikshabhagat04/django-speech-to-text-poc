const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const clearBtn = document.getElementById("clearBtn");
const transcriptBox = document.getElementById("transcript");
const statusBadge = document.getElementById("status");
const languageLabel = document.getElementById("language");
const feedback = document.getElementById("feedback");
const titleInput = document.getElementById("recordTitle");

let socket = null;
let recorder = null;
let stream = null;
let transcriptText = "";
let detectedLanguage = "unknown";
let recording = false;

function setStatus(text, style) {
    statusBadge.textContent = text;
    statusBadge.className = `badge text-bg-${style}`;
}

function socketUrl() {
    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    return `${scheme}://${window.location.host}/ws/speech/`;
}

async function startRecording() {
    try {
        if (!navigator.mediaDevices || !window.MediaRecorder) {
            throw new Error("Your browser does not support microphone recording.");
        }
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        socket = new WebSocket(socketUrl());
        socket.binaryType = "arraybuffer";

        socket.onopen = () => {
            const options = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
                ? { mimeType: "audio/webm;codecs=opus" }
                : {};
            recorder = new MediaRecorder(stream, options);
            recorder.ondataavailable = async (event) => {
                if (event.data.size && socket && socket.readyState === WebSocket.OPEN) {
                    const buffer = await event.data.arrayBuffer();
                    socket.send(buffer);
                }
            };
            recorder.start(5000);
            recording = true;
            transcriptText = "";
            transcriptBox.textContent = "Listening...";
            languageLabel.textContent = "Detecting...";
            setStatus("Recording", "danger");
            startBtn.disabled = true;
            stopBtn.disabled = false;
            feedback.textContent = "Microphone is active. Speak clearly.";
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "transcription") {
                transcriptText = data.text;
                detectedLanguage = data.language;
                transcriptBox.textContent = transcriptText;
                languageLabel.textContent = detectedLanguage;
            } else if (data.type === "saved") {
                feedback.innerHTML = `Saved successfully. <a href="/record/${data.id}/">View transcription</a>`;
                setStatus("Saved", "success");
                closeRecording();
            } else if (data.type === "error") {
                feedback.textContent = data.message;
            }
        };

        socket.onerror = () => {
            feedback.textContent = "WebSocket connection error. Check the Django server.";
        };
        socket.onclose = () => {
            if (recording) {
                setStatus("Disconnected", "secondary");
                recording = false;
            }
        };
    } catch (error) {
        feedback.textContent = error.message;
        if (stream) stream.getTracks().forEach(track => track.stop());
    }
}

function stopRecording() {
    if (!recorder || !socket) return;
    setStatus("Processing", "warning");
    stopBtn.disabled = true;
    recorder.onstop = () => {
        socket.send(JSON.stringify({
            action: "finish",
            text: transcriptText,
            language: detectedLanguage,
            title: titleInput.value.trim() || "Speech transcription"
        }));
    };
    recorder.stop();
    stream.getTracks().forEach(track => track.stop());
}

function closeRecording() {
    recording = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    if (stream) stream.getTracks().forEach(track => track.stop());
    if (socket && socket.readyState === WebSocket.OPEN) socket.close();
}

startBtn.addEventListener("click", startRecording);
stopBtn.addEventListener("click", stopRecording);
clearBtn.addEventListener("click", () => {
    transcriptText = "";
    transcriptBox.textContent = "Your transcribed words will appear here...";
    languageLabel.textContent = "Not detected";
});
