/**
 * Controller for the webpages that need barcode scanning.
 */

// TODO -- these global variables should be replaced with a Custom Element (see issue #32)
var inputReceivingBarcodeScan = null;
const buttonToInputMapping = {
    "select-scan-1": "barcode-input-1",
    "select-scan-2": "barcode-input-2",
};

document.addEventListener("barcode-scanned", function (e) {
    document.getElementById("scan").innerText = "Barcode Scan Detected: " + e.detail + " on "
        + new Date().toLocaleTimeString() + "\n";
});

document.addEventListener("barcode-scanned", function (e) {
    if (inputReceivingBarcodeScan === null) {
        document.getElementById("scan").innerText += "No element selected ⇒ navigate to new page"
    } else {
        let targetInput = document.getElementById(inputReceivingBarcodeScan);
        targetInput.value = e.detail;
        inputReceivingBarcodeScan = null;
    }
});

$(".select-scan").click(function(e) {
    inputReceivingBarcodeScan = buttonToInputMapping[e.target.id];
});