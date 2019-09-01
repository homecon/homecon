import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-collapse/iron-collapse.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-icon-button/paper-icon-button.js';

import './shared-styles.js';
import './homecon-edit-dialog.js';
import './homecon-web-socket-object.js';
import './widgets/widget-switch.js';
import './widgets/widget-shading.js';
import './widgets/widget-value-input.js';
import './widgets/widget-alarm.js';
import './widgets/widget-clock.js';
import './widgets/widget-date.js';


class HomeconWidget extends PolymerElement {
  static get template() {
    return html`
      <style>
        :host{
          display: inline-block;
          position: relative;
        }
      </style>

      <div id="container" on-edit-widget="editWidget" on-delete="deleteWidget"><div></div></div>
    `;
  }

  static get properties() {
    return {
      class: {
        reflectToAttribute: true,
      },
      key: {
        type: 'String',
      },
      widget: {
        type: 'Object',
      },
      edit: {
        type: 'Boolean',
        value: false,
        observer: 'editChanged'
      }
    };
  }

  static get observers() {
    return [
      'updateWidget(widget.type)'
    ];
  }

  updateWidget(type){

    // console.log('update widget', type, JSON.stringify(this.widget.config))
    var container = this.$.container;
    // import the widget
    //this.importHref( this.resolveUrl(type+'.html'), null, null, true );

    // create the widget and set properties
    var widget = document.createElement('widget-'+type);

    for(var attrname in this.widget.config){
        widget[attrname] = this.widget.config[attrname];
    }

    this.set('widgetinstance', widget);
    // set the host class based on the widget type
    if('classes' in widget){
      this.class = widget.classes;
      this.dispatchEvent(new CustomEvent('class-changed', {'detail': {'class': this.class}}));
    }

    // add the widget to the dom
    container.removeChild(container.firstChild)
    container.appendChild(widget);
  }

  editChanged(newValue){
    if(typeof this.widgetinstance != 'undefined' && this.widgetinstance != {}){
      this.widgetinstance.edit = newValue;
    }
  }

}

window.customElements.define('homecon-widget', HomeconWidget);
