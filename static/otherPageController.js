/**
 * Controller for the webpages that need barcode scanning.
 */

// TODO -- these global variables should be replaced with a Custom Element (see issue #32)
var inputReceivingBarcodeScan = null;
const buttonToInputMapping = {
    "move-slot-form-barcode": "form-move-tray-destination-id",
    "new-crop-form-barcode": "form-new-crop-slot",
};

document.addEventListener("barcode-scanned", function (e) {
    let barcode_text = e.detail;
    if (inputReceivingBarcodeScan === null) {
        window.location.href = "http://example.com/barcode/" + barcode_text + "/"
    } else {
        let targetInput = document.getElementById(inputReceivingBarcodeScan);
        if (target.tagName == "SELECT") {
            targetInput.selectedIndex = barcode_text
        }
        else if (target.tagName == "INPUT") {
            targetInput.value = barcode_text;
        }
        inputReceivingBarcodeScan = null;
    }
});

$(".select-scan").click(function(e) {
    inputReceivingBarcodeScan = buttonToInputMapping[e.target.id];
});