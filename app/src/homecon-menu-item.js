import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

class HomeconMenuItem extends PolymerElement {
  static get template() {
    return html`
      <style>
        :host{
          display: block;
          position: relative;
          width: 100%;
          color: var(--primary-text-color);
          margin-left: 10px;
        }
          a.item{
          display: block;
          position: relative;
          cursor: pointer;
          text-decoration: none;
          height: 50px;
        }
          a.item .icon{
          height: 100%;
        }
          a.item .title{
          display: inline-block;
          font-size: 18px;
          font-family: sans-serif;
          font-weight: 700;
          color: var(--button-text-color);
          text-shadow: 0 1px 0 var(--text-shadow-color);
          margin-left: 10px;
          overflow: hidden;
        }
      </style>
      <a class="item horizontal layout center" href="[[href]]">
        <img class="icon" src="/images/icon/ffffff/[[icon]].png">
        <h1 class="title">[[title]]</h1>
      </a>
    `;
  }

  static get properties() {
    return {
      href:{
        type: 'String'
      },
      title:{
        type: 'String'
      },
      icon:{
        type: 'String'
      },
    };
  }
}

window.customElements.define('homecon-menu-item', HomeconMenuItem);
