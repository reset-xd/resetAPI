var eyetracker = document.getElementById("eyetracker");

function getOffset(el) {
    const rect = el.getBoundingClientRect();
    return {
      left: rect.left + window.scrollX,
      top: rect.top + window.scrollY
    };
  }

// eyetracker.style.marginTop = ((window.screen.height/2) - 300) + "px"
onmousemove = function(e){
    sw = this.window.screen.width;
    sh = this.window.screen.height;
    if(sw/2 > e.clientX && sh/2 < e.clientY){
        eyetracker.src = "/asset/maindownleft.gif";
    }
    else if(sw/2 < e.clientX  && sh/2 <= e.clientY){
        eyetracker.src = "/asset/maindownright.gif";
    }
    else if(sw/2 > e.clientX && sh/2 >= e.clientY){
        eyetracker.src = "/asset/mainupleft.gif";
    }
    else if(sw/2 < e.clientX  && sh/2 > e.clientY){
        eyetracker.src = "/asset/mainupright.gif";
    }
}