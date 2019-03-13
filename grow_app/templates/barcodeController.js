/**
 * Controller for the webpages that need barcode scanning.
 */

// TODO -- Create a more robust barcode parsing function that maps barcodes to slot id's
function parseBarcode(barcode) {
   return barcode.replace(/^0+/, '')  // This removes any leading zeros that the barcode string might have
}

// TODO -- these global variables should be replaced with a Custom Element (see issue #32)
var inputReceivingBarcodeScan = null;
const buttonToInputMapping = {
    "move-slot-form-barcode": "form-move-tray-destination-id",
    "new-crop-form-barcode": "form-new-crop-slot",
};

document.addEventListener("barcode-scanned", function (e) {
    if (inputReceivingBarcodeScan === null) {
        var parsed_barcode = parseBarcode(e.detail)
        window.location = "/slot/" + parsed_barcode + "/"
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