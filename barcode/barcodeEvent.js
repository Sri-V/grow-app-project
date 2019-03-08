/**
 * Code that detects when the Nadamoo YHD-3100 Barcode Scanner interacts with the webpage, and emits a custom event
 * that allows other JavaScripts to respond accordingly.
 */

// FIXME -- eliminate global variables if possible (apply a namespace?)
var barcodeScannerData = ""; // The raw data read from the scanner
var inputStartTime = 0; // Start time of the input
var inputEndTime = 0; // End time of the input
var observedInputSpeed = 0; //Speed of the observed input, measured in milliseconds per keypress
const speedThreshold = 35; // Threshold against which we measure human vs barcode input, also milliseconds per keypress
const scannerPrefix = "{BAR}";

/**
 * When the document registers a keypress, update the text we save from the barcode scanner and emit an event.
 */
$(document).keypress(function (event) {

    console.log("Browser detected the following key:", event.key);

    // Start the timer when the first keypress is detected
    if (barcodeScannerData === "") {
        inputStartTime = performance.now();
        console.log("Recorded start time:", inputStartTime);
    }

    if (event.key === "Enter") {
        inputEndTime = performance.now();
        console.log("Enter hit. Stopping time at:", inputEndTime);
        observedInputSpeed = (inputEndTime - inputStartTime) / (barcodeScannerData.length);
        console.log("Observed input speed is:", observedInputSpeed);
        console.log("Barcode Scanner Data variable is:", barcodeScannerData);
        let detectedScannerPrefix = barcodeScannerData.startsWith(scannerPrefix);
        if (observedInputSpeed <= speedThreshold && detectedScannerPrefix) {
            let parsedBarcodeText = barcodeScannerData.slice(5);
            let barcodeEvent = new CustomEvent("barcode-scanned", { detail: parsedBarcodeText });
            document.dispatchEvent(barcodeEvent);
        }

        resetBarcodeData();
        event.preventDefault();

    } else {
        barcodeScannerData += event.key;
    }
});

document.addEventListener("barcode-scanned", function(e) {
   console.log("Barcode Scan event:", e.detail);
});

/**
 * Reset the global variables used for detection of barcode scans.
 */
function resetBarcodeData() {
    barcodeScannerData = "";
    observedInputSpeed = 0;
    inputStartTime = 0;
    inputEndTime = 0;
}