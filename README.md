# flexfact_tina

This project aims to integrate [Petri nets](https://en.wikipedia.org/wiki/Petri_net) created in [Tina](http://projects.laas.fr/tina) with the [FlexFact simulator](https://fgdes.tf.fau.de/flexfact.html) by leveraging it's Modbus TCP interface. It is important to note that this integration is not a live connection, as it relies on exported `.net` files as input rather than running within Tina itself.

## How transitions should be named

Petri nets operate based on transitions, making them event-driven systems. As such, from the point of view of this script, the names assigned to places don't matter.

However, the names assigned to transitions do: this is what links a Tina transition to a FlexFact event. The way this has been defined is that the name of a transition should match the name of the FlexFact event (details of which you can find on the FlexFact website). However, since Tina (and probably the formal definition of Petri nets) don't permit duplicate transition names, anything after the character "X" in a transition name (except ";" - more details later) is ignored. This means you can call your transitions `sf_fdon`, `sf_fdonX` and `sf_fdonXsomereallylongsentence` and they will all be treated as `sf_fdon` when sending an event to FlexFact. While this may not be formally acceptable, it leaves the Petri net much simpler, especially when dealing with forking.

The ";" character at the start of a name ignores that transition, allowing tokens to pass freely. This is helpful when using a transition to explain something.

When used in the middle of a name, ";" separates the name into component parts, so you can use, for example, `sf_fdon;cb1_bm+` to trigger the `sf_fdon` and `cb1_bm+` events. Be warned that this hasn't been well tested.

## How to export your Petri nets

Click on "Edit → Textify" and a plain text equivalent of your Petri net will be shown. Click on "File → save" and save this output in a `.net` file.

## Running the controller

Install the dependencies with `pip install -r requirements.txt`, or simply install pymodbus with `pip install pymodbus`.

Select modbus as the communication protocol and start the simulation in FlexFact and run the controller with `python src/main.py -d your_modbus_config.dev -n your_tina_export.net`. You can also use `python src/main.py -h` for more info.

## Limitations

Because this is basically a loop running every 10ms (or whatever you use), it can cause the simulator to slow a little. There may be a more efficient way of implementing this, but it would require significant reworking of the idea.

Since Modbus involves checking the values of an input, this system initially works with values, rather than transitions. This is fixed by using the checkTransition function.

## License

This project was developed as part of a module project at the Universidade Federal do Rio Grande do Sul and is licensed under the MIT license.
