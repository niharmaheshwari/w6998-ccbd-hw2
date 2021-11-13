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

// // Sync the text inside the text area with the noteContent variable.
// noteTextarea.on('input', function() {
//     noteContent = $(this).val();
// })

    // $('#save-note-btn').on('click', function(e) {
    //     recognition.stop();

    //     if(!noteContent.length) {
    //         instructions.text('Could not save empty note. Please add a message to your note.');
    //     }
    //     else {
    //         // Save note to localStorage.
    //         // The key is the dateTime with seconds, the value is the content of the note.
    //         saveNote(new Date().toLocaleString(), noteContent);

    //         // Reset variables and update UI.
    //         noteContent = '';
    //         renderNotes(getAllNotes());
    //         noteTextarea.val('');
    //         instructions.text('Note saved successfully.');
    //     }

    // })


    // notesList.on('click', function(e) {
    //     e.preventDefault();
    //     var target = $(e.target);

    //     // Listen to the selected note.
    //     if(target.hasClass('listen-note')) {
    //         var content = target.closest('.note').find('.content').text();
    //         readOutLoud(content);
    //     }

    //     // Delete note.
    //     if(target.hasClass('delete-note')) {
    //         var dateTime = target.siblings('.date').text();
    //         deleteNote(dateTime);
    //         target.closest('.note').remove();
    //     }
    // });



    // /*-----------------------------
    //       Speech Synthesis
    // ------------------------------*/

    // function readOutLoud(message) {
    //     var speech = new SpeechSynthesisUtterance();

    //     // Set the text and voice attributes.
    //     speech.text = message;
    //     speech.volume = 1;
    //     speech.rate = 1;
    //     speech.pitch = 1;

    //     window.speechSynthesis.speak(speech);
    // }



    // /*-----------------------------
    //       Helper Functions
    // ------------------------------*/

    // function renderNotes(notes) {
    //     var html = '';
    //     if(notes.length) {
    //         notes.forEach(function(note) {
    //             html+= `<li class="note">
    //         <p class="header">
    //           <span class="date">${note.date}</span>
    //           <a href="#" class="listen-note" title="Listen to Note">Listen to Note</a>
    //           <a href="#" class="delete-note" title="Delete">Delete</a>
    //         </p>
    //         <p class="content">${note.content}</p>
    //       </li>`;
    //         });
    //     }
    //     else {
    //         html = '<li><p class="content">You don\'t have any notes yet.</p></li>';
    //     }
    //     notesList.html(html);
    // }


    // function saveNote(dateTime, content) {
    //     localStorage.setItem('note-' + dateTime, content);
    // }


    // function getAllNotes() {
    //     var notes = [];
    //     var key;
    //     for (var i = 0; i < localStorage.length; i++) {
    //         key = localStorage.key(i);

    //         if(key.substring(0,5) == 'note-') {
    //             notes.push({
    //                 date: key.replace('note-',''),
    //                 content: localStorage.getItem(localStorage.key(i))
    //             });
    //         }
    //     }
    //     return notes;
    // }


    // function deleteNote(dateTime) {
    //     localStorage.removeItem('note-' + dateTime);
    // }