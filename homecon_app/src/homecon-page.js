import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

class HomeconPage extends PolymerElement {
  static get template() {
    return html`
       <style>
          :host{
            display: block;
            padding: 20px;
          }
          @media only screen and (max-width: 768px) {
            :host{
                padding: 4px;
              }
          }
        </style>

        <slot>
        </slot>
    `;
  }
}

window.customElements.define('homecon-page', HomeconPage);
