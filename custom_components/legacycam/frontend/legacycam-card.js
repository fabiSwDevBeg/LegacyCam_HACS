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
          <div class="wrapper">

            <img id="preview" />

            <button class="flash" id="flashBtn">⚡</button>

          </div>

          <div class="overlay hidden" id="overlay">
            <div class="overlay-content">

              <button class="close" id="closeBtn">✕</button>

              <img id="stream" />

              <button class="flash overlay-flash" id="flashBtn2">⚡</button>

            </div>
          </div>

        </ha-card>
      `;

      this.content = true;

      this.updatePreview();

      this.querySelector("#preview").onclick = () => {
        const overlay = this.querySelector("#overlay");
        const stream = this.querySelector("#stream");

        stream.src = this.config.stream;

        overlay.classList.remove("hidden");
      };

      this.querySelector("#closeBtn").onclick = () => {
        this.querySelector("#overlay").classList.add("hidden");
        this.querySelector("#stream").src = "";
      };

      const toggleFlash = () => {
        const entity = this.config.flash_entity;
        const state = this._hass.states[entity].state;

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

  updatePreview() {
    const img = this.querySelector("#preview");

    const cam = this._hass.states[this.config.entity];
    if (!cam) return;

    img.src = cam.attributes.entity_picture || this.config.snapshot;

    img.style.transform = `rotate(${this.config.rotation || 0}deg)`;
  }

  getCardSize() {
    return 3;
  }

  // 👇 IMPORTANTISSIMO: abilita editor UI
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