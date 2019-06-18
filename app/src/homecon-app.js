import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import { setPassiveTouchGestures, setRootPath } from '@polymer/polymer/lib/utils/settings.js';
import '@polymer/app-layout/app-drawer/app-drawer.js';
import '@polymer/app-layout/app-drawer-layout/app-drawer-layout.js';
import '@polymer/app-layout/app-header/app-header.js';
import '@polymer/app-layout/app-header-layout/app-header-layout.js';
import '@polymer/app-layout/app-scroll-effects/app-scroll-effects.js';
import '@polymer/app-layout/app-toolbar/app-toolbar.js';
import '@polymer/app-route/app-location.js';
import '@polymer/app-route/app-route.js';
import '@polymer/iron-pages/iron-pages.js';
import '@polymer/iron-selector/iron-selector.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-meta/iron-meta.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import './homecon-web-socket.js';
import './homecon-states.js';
import './homecon-authentication.js';
import './homecon-pages-menu.js';
import './homecon-menu-item.js';

// Gesture events like tap and track generated from touch will not be
// preventable, allowing for better scrolling performance.
setPassiveTouchGestures(true);

// Set Polymer's root path to the same value we passed to our service worker
// in `index.html`.
setRootPath(HomeconAppGlobals.rootPath);

class HomeconApp extends PolymerElement {
  static get template() {
    return html`
      <style include="iron-flex iron-flex-alignment">
        :host {
          display: block;
          --toolbar-background-color: #000000;
          --dialog-background-color: #060606;
          --primary-background-color: #080808;
          --secondary-background-color: #0d0d0d;
          --tertiary-background-color: #0f0f0f;

          --primary-text-color: #ffffff;
          --secondary-text-color: #aaaaaa;

          --text-shadow-color: #111111;

          --primary-color: #f79a1f;

          --menu-item-background-color: #333333;
          --menu-item-text-color: #ffffff;
          --menu-item-border-color: #1f1f1f;
          --menu-item-background-color-hover: #373737;

          --button-background-color: #141414;
          --button-text-color: #ffffff;

          --header-background-color: #ffffff;
          --header-background-color-hover: #ededed;
          --header-text-color: #333333;
          --header-text-shadow-color: #f3f3f3;
          --header-border-color: #dddddd;

          --paper-dialog-background-color: var(--secondary-background-color);
          --paper-dialog-color: var(--primary-text-color);

          color: var(--primary-text-color);
        }

        app-header {
          position: fixed;
          top: 0;
          right: 0;
          left: 0;
          background-color: var(--toolbar-background-color);
          color: var(--primary-text-color);
          box-shadow: 0px 2px 2px 0px rgba(0, 0, 0, 0.5);
          z-index: 102;
        }

        app-header paper-icon-button{
          --paper-icon-button-ink-color: white;
        }

        app-header .title{
          margin-left: 10px;
        }

        app-header .title img{
          height: 50px;
          margin-right: 10px;
        }
        app-header .title a:link, app-header .title a:visited, app-header .title a:hover, app-header .title a:active{
          text-decoration: none;
          color: var(--primary-text-color);
        }

        app-drawer{
          display: none;
          z-index: 101;
        }

        app-drawer.login{
          display: none;
        }

        .drawer-content{
          width: 100%;
          height: 100%;
          margin-top: 64px;
          background-color: var(--secondary-background-color);
          box-shadow: 2px 2px 2px 0px rgba(0, 0, 0, 0.3);
          /*overflow-y: scroll;*/
          /*-webkit-overflow-scrolling: touch;*/
        }

        .drawer-toggle{
          display: none;
        }

        .drawer-content.persistent{
          position: fixed;
          top: 0;
          bottom: 0;
          width: 40%;
          z-index: 2;
        }

        .drawer-content.persistent.login{
          display: none;
        }

        .main-content{
          position: relative;
          margin-left: 40%;
          margin-top: 64px;
          background-color: var(--primary-background-color);
        }

        .main-content.login{
            margin-left: 0px;
        }

        @media (max-width: 767px){
          .drawer, .drawer-toggle {
            display: block;
          }
          .main-content {
            margin-left: 0px;
          }
          .drawer-content.persistent{
            display: none;
          }
        }
      </style>

      <app-location route="{{route}}" url-space-regex="^[[rootPath]]">
      </app-location>

      <app-route route="{{route}}" pattern="[[rootPath]]:page" data="{{routeData}}" tail="{{subroute}}">
      </app-route>

      <homecon-authentication></homecon-authentication>
      <homecon-web-socket connected="{{connected}}"></homecon-web-socket>
      <homecon-states-master></homecon-states-master>

      <iron-meta key="edit" value="{{edit}}"></iron-meta>

      <!-- Header -->
      <app-header fixed shadow class$="[[loginClass]]">
        <app-toolbar>
          <paper-icon-button class="drawer-toggle" icon="icons:menu" on-tap="_toggleDrawer"></paper-icon-button>
          <div class="title"><a class="horizontal layout center home" href="/pages/home/home"><img src="/images/manifest/icon-144x144.png">Homecon</a></div>
          <div class="flex"></div>
          <paper-icon-button class="menu-toggle" icon="icons:more-vert" on-tap="_toggleMenu"></paper-icon-button>
        </app-toolbar>

        <!-- Menu -->
        <paper-dialog id="menu" class$="menu" horizontal-align="right" vertical-allign="top">
          <homecon-menu-item title="States" icon="edit_settings" href="/states"></homecon-menu-item>
          <homecon-menu-item title="Settings" icon="edit_settings" href="/settings"></homecon-menu-item>
          <homecon-menu-item title="Users" icon="homecon_users" href="/users"></homecon-menu-item>
          <homecon-menu-item title="Editor" icon="pagebuilder_pagebuilder" href="/editor"></homecon-menu-item>
          <homecon-menu-item title="Logout" icon="homecon_logout" href="#" on-tap="logout"></homecon-menu-item>
        </paper-dialog>
      </app-header>


      <!-- Drawer -->
      <app-drawer id="drawer" class$="drawer [[loginClass]]">
        <div class="drawer-content">
          <!-- Pages menu -->
          <homecon-pages-menu groups="[[menuGroups]]"></homecon-pages-menu>
        </div>
      </app-drawer>

      <div class$="drawer-content persistent [[loginClass]]">
        <!-- Pages menu -->
        <homecon-pages-menu groups="[[menuGroups]]"></homecon-pages-menu>
      </div>


      <!-- Main -->
      <div class$="main-content [[loginClass]]">
        <iron-pages selected="[[page]]" attr-for-selected="name">
          <view-login name="login"></view-login>
          <view-pages name="pages" route="[[subroute]]"></view-pages>
          <view-states id="states" name="states"></view-states>
          <view-settings id="settings" name="settings"></view-settings>
          <view-editor name="editor" pages-path="{{pagesPath}}"></view-editor>
          <view-users name="users"></view-users>
        </iron-pages>
      </div>
    `;
  }

  static get properties() {
    return {
      page: {
        type: String,
        reflectToAttribute: true,
        observer: '_pageChanged'
      },
      routeData: Object,
      subroute: Object
    };
  }

  static get observers() {
    return [
      '_routePageChanged(routeData.page)'
    ];
  }

  ready() {
    super.ready();
  }

  _routePageChanged(page) {
     // Show the corresponding page according to the route.
     //
     // If no page was found in the route data, page will be an empty string.
     // Show 'view1' in that case. And if the page doesn't exist, show 'view404'.
    if (!page) {
      this.page = 'login';
    } else if (['pages', 'states'].indexOf(page) !== -1) {
      this.page = page;
    } else {
      this.page = 'view404';
    }

    // Close a non-persistent drawer when the page & route are changed.
    if (!this.$.drawer.persistent) {
      this.$.drawer.close();
    }
  }

  _pageChanged(page) {
    switch (page) {
      case 'login':
        import('./my-view1.js');
        break;
      case 'pages':
        import('./view-pages.js');
        break;
      case 'states':
        import('./view-states.js');
        break;
      case 'view3':
        import('./my-view3.js');
        break;
      case 'view404':
        import('./my-view404.js');
        break;
    }
  }

  _closeDrawer(){
    this.$.drawer.close();
  }

  _toggleDrawer(){
    this.$.drawer.toggle();
  }

  _closeMenu(){
    this.$.menu.close();
  }

  _toggleMenu(){
    this.$.menu.toggle();
  }

}

window.customElements.define('homecon-app', HomeconApp);
