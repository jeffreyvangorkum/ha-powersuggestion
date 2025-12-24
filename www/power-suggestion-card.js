class PowerSuggestionCard extends HTMLElement {
    set hass(hass) {
        if (!this.content) {
            const card = document.createElement('ha-card');
            card.header = 'Power Suggestion';
            this.content = document.createElement('div');
            this.content.style.padding = '0 16px 16px';
            card.appendChild(this.content);
            this.appendChild(card);
        }

        const entityId = this.config.entity;
        const state = hass.states[entityId];

        if (!state) {
            this.content.innerHTML = `
        <p class="error">Entity not found: ${entityId}</p>
      `;
            return;
        }

        const cycles = state.attributes.cycles_detected || [];
        const isAnalyzing = state.attributes.analyzing;

        let cyclesHtml = '<h3>Detected Cycles</h3>';
        if (cycles.length === 0) {
            cyclesHtml += '<p>No cycles detected yet.</p>';
        } else {
            cyclesHtml += '<ul>';
            cycles.forEach(cycle => {
                cyclesHtml += `
          <li>
            <b>${cycle.name || 'Unknown'}</b>: 
            ${cycle.duration_minutes} mins, ${cycle.total_energy_kwh} kWh
            <br/><span style="font-size: 0.8em; color: var(--secondary-text-color)">${cycle.start}</span>
          </li>`;
            });
            cyclesHtml += '</ul>';
        }

        this.content.innerHTML = `
      <style>
        .error { color: var(--error-color); }
        ul { padding-left: 20px; }
        li { margin-bottom: 8px; }
      </style>
      <div>
        Status: <b>${state.state} cycles</b> ${isAnalyzing ? '(Analyzing...)' : ''}
      </div>
      <div>
        ${cyclesHtml}
      </div>
    `;
    }

    setConfig(config) {
        if (!config.entity) {
            throw new Error('You need to define an entity');
        }
        this.config = config;
    }

    getCardSize() {
        return 3;
    }
}

customElements.define('power-suggestion-card', PowerSuggestionCard);
window.customCards = window.customCards || [];
window.customCards.push({
    type: "power-suggestion-card",
    name: "Power Suggestion Card",
    preview: true,
    description: "Card to view Power Suggestion cycles"
});
