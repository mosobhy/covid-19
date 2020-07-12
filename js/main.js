let myRecord = document.querySelector("#record");
let stopRecord = document.querySelector("#stop");


myRecord.addEventListener("click", function () {
 
  record();
});

stopRecord.addEventListener("click", function(){
  stopFunction();
})


let mic, recorder, soundFile;
let state = 0;


function setup() {

  // create an audio in
  mic = new p5.AudioIn();

  // create a sound recorder
  recorder = new p5.SoundRecorder();

  // this sound file will be used to
  // playback & save the recording
    soundFile = new p5.SoundFile();
  
      // connect the mic to the recorder
  recorder.setInput(mic);

}

function record()
{
  mic.start();
 // prompts user to enable their browser mic
  if (state === 0 && mic.enabled) {
    
    recorder.record(soundFile);  
    state++;
  }

}

function stopFunction() {

  if (state <= 1)
  {
    mic.stop();
    recorder.stop();
    state++;
    }
    else if (state === 2) {
      soundFile.play(); // play the result!
      state++;
    }
 
}