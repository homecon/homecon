import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';

class HomeconPageHeader extends PolymerElement {
  static get template() {
    return html`
       <style include="iron-flex iron-flex-alignment">
        :host{
          color: var(--primary-text-color);
        }
        .icon{
          height: 60px;
        }
        .title{
          margin: 5px 5px 5px 20px;
          font-size: 2em;
          font-weight: 700;
        }
      </style>

      <div class="horizontal layout">
        <img class="icon" src="[[_parseIcon(icon)]]">
        <h1 class="title flex">[[title]]</h1>
        <template is="dom-if" if="[[_hasWidget(widget)]]">
          <div class="widget">
            20°C
          </div>
        </template>
      </div>
    `;
  }

  static get properties() {
    return {
      title: {
        type: String,
      },
      icon: {
        type: String,
      },
      widget: {
        type: Object,
      },
    };
  }

  _hasWidget(widget){
    return !(widget=={})
  }

  _parseIcon(icon){
    if(icon==''){
      return '/images/icon/ffffff/blank.png';
    }
    else{
      return '/images/icon/ffffff/'+ icon +'.png';
    }
  }

}

window.customElements.define('homecon-page-header', HomeconPageHeader);
