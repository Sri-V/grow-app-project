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
    if (inputReceivingBarcodeScan === null) {
        var barcode_text = e.detail;
        // TODO -- submit a form with the barcode
    } else {
        let targetInput = document.getElementById(inputReceivingBarcodeScan);
        if (target.tagName == "SELECT") {
            targetInput.selectedIndex = parseBarcode(e.detail)
        }
        else if (target.tagName == "INPUT") {
            targetInput.value = parseBarcode(e.detail);
        }
        inputReceivingBarcodeScan = null;
    }
});

$(".select-scan").click(function(e) {
    inputReceivingBarcodeScan = buttonToInputMapping[e.target.id];
});