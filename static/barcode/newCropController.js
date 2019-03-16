/**
 * Controller for the webpages that need barcode scanning.
 */

// TODO -- these global variables should be replaced with a Custom Element (see issue #32)
var inputReceivingBarcodeScan = null;
const buttonToInputMapping = {
    "form-new-crop-barcode-btn": "form-new-crop-barcode-input",
};

document.addEventListener("barcode-scanned", function (e) {
    let barcode_text = e.detail;
    if (inputReceivingBarcodeScan === null) {
        window.location.href = "/barcode/" + barcode_text + "/"
    } else {
        let targetInput = document.getElementById(inputReceivingBarcodeScan);
        targetInput.value = e.detail;
        inputReceivingBarcodeScan = null;
    }
});

$(".select-scan").click(function(e) {
    inputReceivingBarcodeScan = buttonToInputMapping[e.target.id];
});