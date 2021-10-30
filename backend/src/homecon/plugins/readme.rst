Plugins
-------



HomeCon core objects
^^^^^^^^^^^^^^^^^^^^

The lowest level of controlable components are "states".
A state should be linked to a state of the building or it's surroundings.
States can have several datatypes.
The value of every state is stored in the database.
This is done to be able to create states of variables which are not measurable, for instance, a state controling the automatic operation of a shading or not.

A higher level of objects are "components". These are used to define different objects in the building, for instance, a light or a window.
An object can contain references to one or more states.
For example, a light component has a reference to the state of the light, on or off.

States are not meant to be accessed directly, they should be accessed by accessing the corresponding component.


When using the web app components should be easily defineable.
Therefore each plugin must publish a list of components they control.

For each component a list of available component config properties and a list of states must be published as well.
Some of the config properties of the states may be controlable individually, for example a KNX group address to write to when the state changes.
