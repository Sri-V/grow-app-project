/**
 * Controller for the homepage
 */


document.addEventListener("barcode-scanned", function (e) {
    barcode_str = e.detail
    parsed_barcode = barcode_str.parseInt() // # TODO -- Create a more robust barcode parsing function that maps barcodes to slot id's
    window.location = "/slot/" + parsed_barcode + "/"
});

