/**
 * Code that detects when the Nadamoo YHD-3100 Barcode Scanner interacts with the webpage, and emits a custom event
 * that allows other JavaScripts to respond accordingly.
 */

// FIXME -- eliminate global variables if possible (apply a namespace?)
var keypressBuffer = []; //
var rawScannerData = "";
var inputStartTime = null;
var inputEndTime = null;
var observedInputSpeed = 0; // Measured in milliseconds per keypress
const speedThreshold = 35; // Also milliseconds per keypress
const scannerPrefix = "{BAR}";

/**
 * When the document registers a keypress, update the text we save from the barcode scanner and emit an event.
 */
$(document).keypress(function (event) {

    console.log("Browser detected the following key:", event.key);
    appendKeypressBuffer(event.key);

    // If we're currently reading in a barcode stream
    if (barcodeDetectionIsActive()) {
        rawScannerData += event.key;
    } else if (barcodePrefixDetected()) { // Otherwise if we've detected the beginning of a barcode stream
        activateBarcodeDetection();
    }


    // When we reach the end of the barcode stream
    if (barcodeDetectionIsActive() && event.key === "Enter") {

        // Check the stream came in fast enough for a barcode scan
        inputEndTime = performance.now();
        console.log("Stopping time at:", inputEndTime);
        observedInputSpeed = (inputEndTime - inputStartTime) / (rawScannerData.length);
        console.log("Input speed:", observedInputSpeed);



        // If the barcode stream meets all required criteria for speed and contents then emit the event
        if (observedInputSpeed <= speedThreshold) {
            let parsedBarcodeContents = rawScannerData.slice(0, -5);
            console.log("Barcode content is:", parsedBarcodeContents);
            let barcodeEvent = new CustomEvent("barcode-scanned", { detail: parsedBarcodeContents });
            document.dispatchEvent(barcodeEvent);
        }

        // And cleanup afterwards
        resetBarcodeData();
        event.preventDefault();

    }
});

/**
 * Reset the global variables used for detection of barcode scans.
 */
function resetBarcodeData() {
    rawScannerData = "";
    observedInputSpeed = 0;
    inputStartTime = null;
    inputEndTime = null;
}

/**
 * Checks the contents of the keypress buffer to determine if we've registered a barcode scan.
 */
function barcodePrefixDetected() {
    return keypressBuffer.join("") === scannerPrefix;
}

/**
 * Insert a new character into the buffer, keeping no more characters than the length of the scanner's prefix.
 */
function appendKeypressBuffer(key) {
    // Add the character to the end of the keypress buffer
    keypressBuffer.push(key);

    // And if the buffer is now greater than the length of the prefix
    if (keypressBuffer.length > scannerPrefix.length) {
        keypressBuffer.shift();  // Get rid of the oldest character in the buffer
    }
}

/**
 * Sets the global variables necessary to detect an incoming barcode.
 */
function activateBarcodeDetection() {
    resetBarcodeData();
    inputStartTime = performance.now();
    console.log("Barcode prefix detected:", inputStartTime);
}

/**
 * Checks that the keys we're currently processing are possibly part of a barcode.
 */
function barcodeDetectionIsActive() {
    return inputStartTime !== null;
}

