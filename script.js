try {
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition();
}
catch(e) {
    console.error(e);
    $('.no-browser-support').show();
    $('.app').hide();
}

var noteContent = '';
recognition.continuous = true;


recognition.onresult = function(event) {

    var current = event.resultIndex;

    var transcript = event.results[current][0].transcript;
    var mobileRepeatBug = (current == 1 && transcript == event.results[0][0].transcript);

    if(!mobileRepeatBug) {
        noteContent += transcript;
        console.log(noteContent)
        document.getElementById('note-textarea').value = noteContent
    }

    recognition.stop()
};

recognition.onstart = function() {
    console.log("Starting Speech Recognition Service .. ")
}

recognition.onspeechend = function() {
    console.log("Ending Speech Recognition as it could not detect anything for a while ..")
}

recognition.onerror = function(event) {
    console.error("There was an error in the Speech Recognition ..")
    console.error(event.error)
    console.error(event.message)
    if(event.error == 'no-speech') {
        console.log("Error")

        instructions.text('No speech was detected. Try again.');
    };
}

function startRecording() {
    noteContent = ''
    recognition.start();
}

function stopRecording() {
    recognition.stop();
}