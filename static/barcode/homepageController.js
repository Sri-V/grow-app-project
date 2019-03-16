/**
 * Controller for the webpages that need barcode scanning.
 */

document.addEventListener("barcode-scanned", function (e) {
    let barcode_text = e.detail;
    window.location.href = "/barcode/" + barcode_text + "/"
});