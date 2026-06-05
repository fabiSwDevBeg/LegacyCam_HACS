window.customCards = window.customCards || [];

window.customCards.push({
  type: "legacycam-card",
  name: "LegacyCam Card",
  description: "MJPEG camera card with flash control + overlay stream + rotation"
});

if (!customElements.get("legacycam-card-editor")) {
  customElements.define(
    "legacycam-card-editor",
    LegacyCamCardEditor
  );
}