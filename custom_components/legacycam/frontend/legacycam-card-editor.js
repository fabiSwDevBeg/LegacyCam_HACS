class LegacyCamCardEditor extends HTMLElement {

  setConfig(config) {
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.rendered) this.render();
  }

  render() {
    this.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:12px; padding:10px;">

        <label>Camera entity</label>
        <select id="entity"></select>

        <label>Flash entity</label>
        <select id="flash"></select>

        <label>Stream URL</label>
        <input id="stream" type="text" placeholder="http://IP:8080/stream" />

        <label>Rotation</label>
        <select id="rotation">
          <option value="0">0°</option>
          <option value="90">90°</option>
          <option value="180">180°</option>
          <option value="270">270°</option>
        </select>

      </div>
    `;

    this.fillEntities();

    this.querySelector("#entity").value = this.config.entity || "";
    this.querySelector("#flash").value = this.config.flash_entity || "";
    this.querySelector("#stream").value = this.config.stream || "";
    this.querySelector("#rotation").value = this.config.rotation || 0;

    this.querySelectorAll("input, select").forEach(el => {
      el.onchange = () => this.updateConfig();
    });

    this.rendered = true;
  }

  fillEntities() {
    const entities = Object.keys(this._hass.states);

    const camSelect = this.querySelector("#entity");
    const flashSelect = this.querySelector("#flash");

    entities.forEach(e => {
      const opt1 = document.createElement("option");
      opt1.value = e;
      opt1.text = e;

      const opt2 = opt1.cloneNode(true);

      camSelect.appendChild(opt1);
      flashSelect.appendChild(opt2);
    });
  }

  updateConfig() {
    const configEvent = new CustomEvent("config-changed", {
      detail: {
        config: {
          ...this.config,
          entity: this.querySelector("#entity").value,
          flash_entity: this.querySelector("#flash").value,
          stream: this.querySelector("#stream").value,
          rotation: parseInt(this.querySelector("#rotation").value)
        }
      },
      bubbles: true,
      composed: true
    });

    this.dispatchEvent(configEvent);
  }
}

customElements.define("legacycam-card-editor", LegacyCamCardEditor);