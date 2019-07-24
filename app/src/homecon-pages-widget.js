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

class HomeconPagesWidget extends PolymerElement {
  static get template() {
    return html`
      <style>
        :host{
          display: inline-block;
          position: relative;
        }
      </style>

      <homecon-web-socket-object id="websocketWidget" event="pages_widget" key="{{key}}" data="{{widget}}" auto></homecon-web-socket-object>

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
      pagesectionKey: {
        type: 'Number'
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
    console.log('update widget', type, JSON.stringify(this.widget.config))
    var container = this.$.container;
    // import the widget
    //this.importHref( this.resolveUrl(type+'.html'), null, null, true );

    // create the widget and set properties
    var widget = document.createElement('widget-'+type);

    for(var attrname in this.widget.config){
        widget[attrname] = this.widget.config[attrname];
    }

//    if(typeof this.widget.config['initialized'] == 'undefined'){
//    console.log(widget.config)
//
//      console.log(JSON.stringify(widget.config), widget.config)
////      this.$.websocketWidget.send({'config': widget.config});
//    }
//    else{
//      widget.config = this.widget.config;
//    }
    this.set('widgetinstance', widget);

    // set the host class based on the widget type
    if('classes' in widget){
      this.class = widget.classes;
    }

    // add the widget to the dom
    container.removeChild(container.firstChild)
    container.appendChild(widget);
  }

  editWidget(e,d){
    e.stopPropagation()
    this.$.websocketWidget.send({'config':d});
  }

  deleteWidget(e){
    e.stopPropagation();
    this.$.websocketWidget.send(null);
  }

  editChanged(newValue){
    if(typeof this.widgetinstance != 'undefined' && this.widgetinstance != {}){
      this.widgetinstance.edit = newValue;
    }
  }

}

window.customElements.define('homecon-pages-widget', HomeconPagesWidget);
