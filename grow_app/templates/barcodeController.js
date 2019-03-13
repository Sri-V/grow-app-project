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
        var barcode_str = e.detail
        var parsed_barcode = Number(barcode_str) // # TODO -- Create a more robust barcode parsing function that maps barcodes to slot id's
        window.location = "/slot/" + parsed_barcode + "/"
    } else {
        let targetInput = document.getElementById(inputReceivingBarcodeScan);
        targetInput.value = e.detail;
        inputReceivingBarcodeScan = null;
    }
});

$(".select-scan").click(function(e) {
    inputReceivingBarcodeScan = buttonToInputMapping[e.target.id];
});