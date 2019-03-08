/**
 * Code that detects when the Nadamoo YHD-3100 Barcode Scanner interacts with the webpage, and emits a custom event
 * that allows other JavaScripts to respond accordingly.
 */

// FIXME -- eliminate global variables if possible (apply a namespace?)
var barcodeScannerData = ""; // The raw data read from the scanner
var start = 0; //Start time of the input
var inputSpeed = 0; //Speed of the input
const scannerPrefix = "{BAR}";

/**
 * When the document registers a keypress, get the data from the scanner if the form field is not focused.
 */
$(document).keypress(function (event) {
    // If barcodeScannerData is empty start the timer
    if (barcodeScannerData === "") {
        start = performance.now();
    }

    let keyPressedWasEnter = event.key === "Enter";

    // If a keypress other than enter is received store the data in the variable
    if (!keyPressedWasEnter) {
        barcodeScannerData += event.key;
        // If the keypress event is enter, stop the timer
    } else {
        inputSpeed = (performance.now() - start) / (barcodeScannerData.length);
        let inputIsActive = document.activeElement.tagName !== "INPUT";
        let detectedScannerPrefix = barcodeScannerData.startsWith(scannerPrefix);
        //If the input Speed less thsn 33 ms, the input has the barcode prefix and there is no form field focused show the data from no form field
        if (inputSpeed <= 33 && inputIsActive && detectedScannerPrefix) {
            document.getElementById("scan").innerHTML = barcodeScannerData.slice(5) + " Scanner detected no form";
            barcodeScannerData = "";
            inputSpeed = 0;
        }

        // Empty variable and prevent enter to submit the form
        barcodeScannerData = "";
        event.preventDefault();
        return false;
    }
    return true;
});

/**
 * When the form's submit button is clicked, determine the source of barcode input and respond accordingly.
 */
document.getElementById("submit").onclick = function (event) {
    let formInputData = document.getElementById("input").value;
    // if there is data in the variable, determine if the input came from user or scanner
    if (formInputData !== "") {
        //If the input Speed is 20 to 33 ms and the input has the barcode prefix
        if (inputSpeed <= 33 && formInputData.startsWith(scannerPrefix)) {
            document.getElementById("scan").innerHTML = formInputData.slice(5) + " Scanner detected from form";
        } else {
            document.getElementById("scan").innerHTML = formInputData + " Came from user ";
        }
        // If submit was clicked with the form field empty inform the user
        //FIXME -- change it to throw an error
    } else {
        document.getElementById("scan").innerHTML = "The form field is empty"
    }


    // Finally reset the data variable and the contents of the form field
    // FIXME -- this should be a separate event handler, eventually in the controller
    barcodeScannerData = "";
    let inputElements = document.getElementsByTagName('input');
    for (let i = 0; i < inputElements.length; i++) {
        if (inputElements[i].type == "text") {
            inputElements[i].value = "";
        }
    }
};