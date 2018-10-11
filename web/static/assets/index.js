// TODO deze javascript is echt een tering zooi, nergens documentatie en alles in een bestand gesmeten. Dit moet effe iemand opruimen.
var x, y, l = 0.0, r = 0.0;
var multiplier = 3.5;
// TODO eigenlijk moet flashlight (net als vele andere dingen hier) haar eigen class hebben.
// TODO lampstatus moet gevraagt worden van de server
// TODO alle variabelen worden met `var` aangemaakt. Het is netter om het met `let` te doen.
let flashlightStatus = 0;
let flashlightDOM = document.querySelector(".buttonFlashlight");

// wat is dit?
window.requestAnimationFrame = window.requestAnimationFrame
	|| window.webkitRequestAnimationFrame
	|| window.mozRequestAnimationFrame
	|| function(callback) { window.setTimeout(callback, 1000 / 60);};

var inputObject = {
    "up": {
        "key": ["KEY_W", "UP_ARROW"],
        "pad": ["DPAD_UP", "RIGHT_TRIGGER"]
    },
    "down": {
        "key": ["KEY_S", "DOWN_ARROW"],
        "pad": ["DPAD_DOWN", "LEFT_TRIGGER"],
        "axes": ["LEFT_Y"]
    },
    "left": {
        "key": ["KEY_A", "LEFT_ARROW"],
        "pad": ["DPAD_LEFT"]
    },
    "right": {
        "key": ["KEY_D", "RIGHT_ARROW"],
        "pad": ["DPAD_RIGHT"],
        "axes": ["LEFT_X"]
    },
    "flashlight": {
        "key": ["KEY_F"],
        "pad": ["BUTTON_X"]
    }
};
// What controller to lisen to
var controllerIndex = 0;
var topSpeed = 255;
// our input objects
var up = new Input.Input(inputObject.up, controllerIndex);
var down = new Input.Input(inputObject.down, controllerIndex);
var left = new Input.Input(inputObject.left, controllerIndex);
var right = new Input.Input(inputObject.right, controllerIndex);
var flashLight = new Input.Input(inputObject.flashlight, controllerIndex, flashlightDOM);
var webSocket = new WebSocket("ws://"+window.location.hostname+":"+window.location.port);

// up
up.press = function() {
	l = topSpeed * this.value;
	r = topSpeed * this.value;
	updateRL();

};
up.release = function() {
    if (down.isUp) {
    	l = 0;
    	r = 0;
        updateRL();
    }
    else down.press();
};

// down
down.press = function() {
    l = -topSpeed * this.value;
    r = -topSpeed * this.value;
    updateRL();
};
down.release = function() {
    if (down.isUp) {
        l = 0;
        r = 0;
        updateRL();
    }
    else down.press();
};

// left
left.press = function() {
    l = -topSpeed * this.value;
    r = topSpeed * this.value;
    updateRL();
};
left.release = function() {
    if (down.isUp) {
        l = 0;
        r = 0;
        updateRL();
    }
    else down.press();
};

// right
right.press = function() {
    l = topSpeed * this.value;
    r = -topSpeed * this.value;
    updateRL();
};
right.release = function() {
    if (down.isUp) {
        l = 0;
        r = 0;
        updateRL();
    }
    else down.press();
};

// flashlight

flashLight.press = function() {
//    deze is nodig omdat anders dingen gaan crashen.
};
flashLight.release = function() {
    // TODO documentatie
    if (flashlightStatus) {
        // TODO lampstatus moet gedefineerd worden door te vragen aan de server of hij aanstaat. En dan de output flippen zodat hij echt toggled.
        flashlightStatus = 0;
        flashlightDOM.classList.add("active");
    } else {
        flashlightStatus = 1;
        flashlightDOM.classList.remove("active");
    }
    send("lamp", flashlightStatus);
};


webSocket.onopen = function (){
    // waarom word deze hier aangeroepen?
    callLoop();
};

webSocket.onclose = function() {
//    TODO proberen opnieuw verbinding te maken.
};

webSocket.onerror = function() {
//    TODO error handeling.
};

webSocket.onmessage = function (event) {
    //TODO error validation.
    console.log(event.data);
};


function callLoop(){
    // TODO documentatie
    // waarom heet deze functie loop als hij niet loopt?
    var le = l.toFixed(0);
    var ri = r.toFixed(0);
    // TODO deze moet alleen data versturen als er veraderingen zijn.
    send("motor", {
        left: le,
        right: ri
    });
}

function updateRL(){
    // TODO is het nodig dat de gebruiker ziet welke waarde hij heeft ingevoerd?
    $("#l")[0].innerHTML = l.toFixed(1);
    $("#r")[0].innerHTML = r.toFixed(1);
    callLoop();
}

/**
 * @param num - entered number
 * @param min - what is considered minimum
 * @param max - what is considered maximum
 * @returns min or max - Checks if num is closer to max or to min, returns accordingly.
 */
function clamp(num, min, max) {
  //  TODO documentatie beschrijving, weet nog steeds niet waar het handig voor is.
  return num <= min ? min : num >= max ? max : num;
}

function move(movedX, movedY){
    // TODO documenatie
	r = movedY;
	l = movedY;

	if(movedX < 0){
		r -= movedX;
	}else if(movedX > 0){
		l -= movedX;
	}

	r *= multiplier;
	l *= multiplier;

	r = clamp(r, -255, 255);
	l = clamp(l, -255, 255);

	updateRL();
}

// TODO ondersteuning voor muis, of het moet weg op desktop.
$(".joystick")[0].addEventListener('touchstart', function(e) {
	x = e.touches[0].clientX;
	y = e.touches[0].clientY;

	$(".joystick").addClass("active");
}, false);

$(".joystick")[0].addEventListener('touchmove', function(e) {
	var movedX, movedY;

	movedX = x - e.touches[0].clientX;
	movedY = y - e.touches[0].clientY;

	move(movedX, movedY);
}, false);


$(".joystick").on('touchend touchcancel', function() {
	move(0.0, 0.0);

	$(".joystick").removeClass("active");
});

$( ".toggle" ).click(function() {
	$(this).toggleClass("active");
});


function send(request, data) {
    // TODO documentatie
    let key = "1234";
    webSocket.send(JSON.stringify(
        {
            "key": key,
            "request": request,
            // TODO data moet optioneel zijn
            "data": data
        }
    ));
//    TODO callback.
}

