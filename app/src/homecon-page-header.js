import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import './homecon-widget.js';

class HomeconPageHeader extends PolymerElement {
  static get template() {
    return html`
       <style include="iron-flex iron-flex-alignment">
        :host{
          color: var(--primary-text-color);
        }
        .header{
          margin-bottom: 25px;
        }
        .icon{
          height: 60px;
        }
        .title{
          margin: 5px 5px 5px 20px;
          font-size: 2em;
          font-weight: 700;
        }
        .widget{
          margin-top: 15px;
          margin-right: 15px;
        }
      </style>

      <div class="horizontal layout header">
        <img class="icon" src="[[_parseIcon(icon)]]">
        <h1 class="title flex">[[title]]</h1>
        <template is="dom-if" if="[[_hasWidget(widget)]]">
          <div class="widget">
            <homecon-widget widget="{{widget}}" edit="{{edit}}"></homecon-widget>
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
