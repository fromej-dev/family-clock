class FamilyClockCard extends HTMLElement {
  setConfig(config) {
    this._config = config || {};
  }

  set hass(_hass) {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
    }
    if (!this._iframe) {
      const height = this._config.height || '800px';
      this._iframe = document.createElement('iframe');
      this._iframe.src = `/local/family_clock/family-clock.html?v=1.2.0`;
      this._iframe.style.cssText = `width:100%;height:${height};border:none;display:block;`;
      this._iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-forms allow-popups');
      this.shadowRoot.appendChild(this._iframe);
    }
  }

  getCardSize() {
    return Math.ceil(parseInt(this._config?.height || '800') / 50);
  }

  static getStubConfig() {
    return {};
  }
}

customElements.define('family-clock-card', FamilyClockCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'family-clock-card',
  name: 'Family Clock',
  description: 'A Weasley-style enchanted family clock — weekly schedule dashboard',
  preview: false,
});
