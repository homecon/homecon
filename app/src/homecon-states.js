import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

import '@polymer/iron-meta/iron-meta.js';

import './homecon-web-socket-object.js';

(function() {

  let statesObject = null;

  class HomeconStatesMaster extends PolymerElement {
    static get template() {
      return html`
        <style>
          :host{
            display: block;
          }
        </style>

        <homecon-web-socket-object event="state_list" key="" data="{{states}}" auto>
        </homecon-web-socket-object>

        <iron-meta key="states" value="{{states}}"></iron-meta>
      `;
    }

    static get properties() {
      return {
        states: {
          type: Array,
          value: () => []
        },
        subscribers: {
          type: Array,
          value: () => []
        }
      };
    }

    static get observers() {
      return [
        'statesChanged(states.*)'
      ]
    }

    constructor() {
      super();
      if(!statesObject){
        statesObject = this;
      }
    }

    register(subscriber) {
      this.subscribers.push(subscriber);
      subscriber.states = this.states;
      subscriber.notifyPath('states');
    }

    unregister(subscriber) {
      var i = this.subscribers.indexOf(subscriber);
      if (i > -1) this.subscribers.splice(i, 1)
    }

    statesChanged(change) {
      for(var i = 0; i < this.subscribers.length; i++) {
        this.subscribers[i].states = this.states
        this.subscribers[i].notifyPath('states');
        // FIXME ref https://www.captaincodeman.com/2017/07/06/managing-state-in-polymer-20-beyond-parent-child-binding
      }
    }
  }

  window.customElements.define('homecon-states-master', HomeconStatesMaster);


  class HomeconStates extends PolymerElement {

    static get properties() {
      return {
        states: {
          type: Array,
          notify: true
        }
      }
    }

    connectedCallback() {
      super.connectedCallback();
      statesObject.register(this);
    }

    disconnectedCallback() {
      super.disconnectedCallback();
      statesObject.unregister(this);
    }
  }

  window.customElements.define('homecon-states', HomeconStates);
}());