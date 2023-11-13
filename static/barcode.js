function generateBarcode(elementId, ean) {
    if (ean !== "0") {
        JsBarcode(`#${elementId}`, ean);
    }
}