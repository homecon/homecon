HomeCon
=======

Control all your home installations using state of the art control algorithms and visualize the results

HomeCon is intended to have the conn over the entire energy management of your home and direct it in the best possible way.
Not only HomeCon has the conn but you do. As the software is entirely local (no information gets sent from your home to the web) you can rest assured that your privacy is respected.
HomeCon's intention is also to go further than just controlling the heating of your home. It will control heating, cooling, shading, ventilation,... and other appliances.
All this is done using an integrated optimization of the operation of all your systems, taking constraints in the future and forecasts into account.


The goal of the project is to have an open source, user friendly control system for a domestic building, including an integrated Model Predictive Control algorithm to control shading, heating, ventilation and other appliances based on weather and energy price predictions and availability of renewable energy in the regional electricity system.


Check the project `documentation <https://pythonhosted.org/homecon/>`_ for a more detailed description and installation instructions.



Installation
------------
..code::

  mkdir homecon
  cd homecon
  python3 -m venv env
  source env/bin/activate
  pip install wheel
  pip install homecon-0.0.0.tar.gz


Running
-------
..code::

  python -m homecon
