import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import './shared-styles.js';
import './homecon-pages-page.js';

class ViewPages extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles">
        :host {
          display: block;
        }
      </style>

      <app-route route="{{route}}" pattern="/:group/:page" data="{{routeData}}" tail="{{subroute}}"></app-route>

      <homecon-pages-page path="{{path}}" edit="{{edit}}"></homecon-page>
    `;
  }

  static get properties() {
    return {
      path: {
        type: String,
        reflectToAttribute: true,
      },
      group: {
        type: String,
        reflectToAttribute: true,
      },
      page: {
        type: String,
        reflectToAttribute: true,
      },
      routeData: Object,
      route: Object
    };
  }

  static get observers() {
    return [
      '_routePageChanged(routeData)'
    ];
  }

  _routePageChanged(routeData){
    if( typeof routeData.group == 'undefined' || typeof routeData.page == 'undefined'){
        this.group = 'home';
        this.page = 'home';
    }
    else{
        this.group = routeData.group;
        this.page = routeData.page;
    }
    this.path = this.group+'/'+this.page;

    // load pages through the websocket only when necessary
    //this._loadPage()
  }

}

window.customElements.define('view-pages', ViewPages);
