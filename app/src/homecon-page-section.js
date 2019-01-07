import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-collapse/iron-collapse.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-icon-button/paper-icon-button.js';

import './shared-styles.js';
import './homecon-edit-dialog.js';

class HomeconPageSection extends PolymerElement {
  static get template() {
    return html`
      <style>
        :host{
          display: block;
          position: relative;
          width: 100%;

          margin: 8px 0px 16px 0px;
        }

        #header{
          display: block;
          font-size: 16px;
          font-family: sans-serif;
          font-weight: 700;

          text-decoration: none;
        }
        #header.collapsible{
          cursor: pointer;

          min-height: 12px;
          padding: 12px 12px 12px 40px;

          background-color: var(--header-background-color);
          border-color: var(--header-border-color);
          border-style: solid;
          border-width: 1px;
          border-radius: 5px;

          color: var(--header-text-color);
          text-shadow: 0 1px 0 var(--header-text-shadow-color);
        }
        #header.collapsible.opened{
          border-radius: 5px 5px 0px 0px;
        }
        #header.collapsible:hover{
          background-color: var(--header-background-color-hover);
        }
        #header.raised{
          position: absolute;
          top: -10px;
          left: 20px;
          color: var(--primary-text-color);
        }
        .content{
          padding: 16px;
        }
        @media only screen and (max-width: 768px) {
          #content{
            padding: 1px;
          }
        }

        .content.collapsible{
          background-color: var(--secondary-background-color);
          border-color: var(--section-border-color);
          border-style: solid;
          border-width: 0px 1px 1px 1px;
          border-radius: 0px 0px 5px 5px;
        }
        .content.raised{
          background-color: var(--secondary-background-color);
          box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12), 0 3px 1px -2px rgba(0, 0, 0, 0.2);
          border-radius: 5px;
        }
        #underline.raised{
          display: none;
        }
        #underline.collapsible{
          display: none;
        }
        #underline.transparent{
          display: none;
        }
        #underline{
          position: relative;
          height: 0px;
          margin-top: 5px;
          margin-bottom: 5px;
          width: 98%;
          border-bottom: solid 1px #ddd;
        }

    </style>

    <a id="header" class$="header {{_headerClass(type)}} {{_openedClass(opened)}}" on-click="changeState">
      {{title}}
    </a>

    <!--<template is="dom-if" if="{_isCollapsible(type)}}">
      <iron-collapse id="collapsible" opened="{{opened}}">
        <div id="content" class$="{{type}}">
          <slot></slot>
        </div>
      </iron-collapse>
    </template>-->

    <div class$="content {{type}}">
      <slot></slot>
    </div>
    `;
  }

  static get properties() {
    return {
      title: {
        type: String,
      },
      type: {
        type: String,
      },
      opened: {
        type: Boolean,
      },
    };
  }

  _openedClass(opened){
    if(opened){
      return "opened"
    }
    else{
      return "";
    }
  }

  _typeChanged(type){
    if(type!='collapsible'){
      this.opened = true;
    }
  }

  _isCollapsible(type){
    return type == 'collapsible';
  }
  _isNotCollapsible(type){
    return type != 'collapsible';
  }

  _headerClass(type){
    if(type!='collapsible'){
      return "raised"
    }
    else{
      return "collapsible";
    }
  }

}

window.customElements.define('homecon-page-section', HomeconPageSection);
