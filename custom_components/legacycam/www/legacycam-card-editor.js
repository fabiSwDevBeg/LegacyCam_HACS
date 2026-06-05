class LegacyCamCardEditor extends HTMLElement {

  setConfig(config) {
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._rendered) this._render();
  }

  _render() {
    this.innerHTML = `
      <div class="lc-editor">

        <label>Camera entity</label>
        <select id="entity"></select>

        <label>Flash entity</label>
        <select id="flash"></select>

        <label>Stream URL</label>
        <input id="stream" type="text" placeholder="http://IP:8080/stream" />

        <label>Snapshot URL</label>
        <input id="snapshot" type="text" placeholder="http://IP:8080/snapshot.jpg" />

        <label>Rotation</label>
        <select id="rotation">
          <option value="0">0°</option>
          <option value="90">90°</option>
          <option value="180">180°</option>
          <option value="270">270°</option>
        </select>

      </div>
    `;

    this._fillEntities();

    this.querySelector("#entity").value = this.config.entity || "";
    this.querySelector("#flash").value = this.config.flash_entity || "";
    this.querySelector("#stream").value = this.config.stream || "";
    this.querySelector("#snapshot").value = this.config.snapshot || "";
    this.querySelector("#rotation").value = this.config.rotation || 0;

    this.querySelectorAll("input, select").forEach(el => {
      el.onchange = () => this._updateConfig();
    });

    this._rendered = true;
  }

  _fillEntities() {
    const entities = Object.keys(this._hass.states);

    const camSelect = this.querySelector("#entity");
    const flashSelect = this.querySelector("#flash");

    entities.forEach(e => {
      const opt1 = document.createElement("option");
      opt1.value = e;
      opt1.textContent = e;

      const opt2 = document.createElement("option");
      opt2.value = e;
      opt2.textContent = e;

      camSelect.appendChild(opt1);
      flashSelect.appendChild(opt2);
    });
  }

  _updateConfig() {
    this.dispatchEvent(new CustomEvent("config-changed", {
      detail: {
        config: {
          ...this.config,
          entity: this.querySelector("#entity").value,
          flash_entity: this.querySelector("#flash").value,
          stream: this.querySelector("#stream").value,
          snapshot: this.querySelector("#snapshot").value,
          rotation: parseInt(this.querySelector("#rotation").value)
        }
      },
      bubbles: true,
      composed: true
    }));
  }
}

customElements.define("legacycam-card-editor", LegacyCamCardEditor);