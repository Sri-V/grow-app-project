/**
 * Controller for the homepage
 */


document.addEventListener("barcode-scanned", function (e) {
    var barcode_str = e.detail
    var parsed_barcode = barcode_str.parseInt() // # TODO -- Create a more robust barcode parsing function that maps barcodes to slot id's
    window.location = "/slot/" + parsed_barcode + "/"
});

