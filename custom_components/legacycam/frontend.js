const loadCard = () => {
  if (!customElements.get("legacycam-card")) {
    import("/hacsfiles/legacycam/legacycam-card.js");
  }

  if (!customElements.get("legacycam-card-editor")) {
    import("/hacsfiles/legacycam/legacycam-card-editor.js");
  }
};

loadCard();

window.customCards = window.customCards || [];
window.customCards.push({
  type: "legacycam-card",
  name: "LegacyCam Card",
  description: "MJPEG camera card with flash + overlay stream + rotation"
});