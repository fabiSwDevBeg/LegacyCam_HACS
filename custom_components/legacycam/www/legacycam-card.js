class LegacyCamCard extends HTMLElement {

  setConfig(config) {
    this.config = {
      rotation: 0,
      ...config
    };
  }

  set hass(hass) {
    this._hass = hass;

    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <div class="lc-wrapper">

            <img id="preview" class="lc-preview" />

            <button class="lc-flash" id="flashBtn">⚡</button>

          </div>

          <div class="lc-overlay hidden" id="overlay">
            <div class="lc-overlay-content">

              <button class="lc-close" id="closeBtn">✕</button>

              <img id="stream" class="lc-stream" />

              <button class="lc-flash-overlay" id="flashBtn2">⚡</button>

            </div>
          </div>

        </ha-card>
      `;

      this.content = true;

      this._updatePreview();

      // OPEN STREAM
      this.querySelector("#preview").onclick = () => {
        const overlay = this.querySelector("#overlay");
        const stream = this.querySelector("#stream");

        stream.src = this.config.stream;
        overlay.classList.remove("hidden");
      };

      // CLOSE
      this.querySelector("#closeBtn").onclick = () => {
        this.querySelector("#overlay").classList.add("hidden");
        this.querySelector("#stream").src = "";
      };

      // FLASH toggle
      const toggleFlash = () => {
        const entity = this.config.flash_entity;
        const state = this._hass.states[entity]?.state;

        this._hass.callService(
          "switch",
          state === "on" ? "turn_off" : "turn_on",
          { entity_id: entity }
        );
      };

      this.querySelector("#flashBtn").onclick = toggleFlash;
      this.querySelector("#flashBtn2").onclick = toggleFlash;
    }
  }

  _updatePreview() {
    const img = this.querySelector("#preview");
    if (!img) return;

    const cam = this._hass.states[this.config.entity];
    if (!cam) return;

    img.src = cam.attributes.entity_picture || this.config.snapshot;

    const rot = this.config.rotation || 0;
    img.style.transform = `rotate(${rot}deg)`;
  }

  getCardSize() {
    return 3;
  }

  // 👉 Lovelace editor
  static getConfigElement() {
    return document.createElement("legacycam-card-editor");
  }

  static getStubConfig() {
    return {
      entity: "",
      flash_entity: "",
      stream: "",
      rotation: 0
    };
  }
}

customElements.define("legacycam-card", LegacyCamCard);