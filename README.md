# FlexFact-Tina

A project to run Petri net files from Tina (http://projects.laas.fr/tina) in the FlexFact simulator (https://fgdes.tf.fau.de/flexfact.html), using the Modbus TCP interface. This is not a live connection, as it doesn't run inside Tina. It simply uses Tina `.net` files as input.

## How to name your transitions

Petri nets work based on transitions. It is therefore an event driven system. From the point of view of this script, therefore, the name you choose to give your places doesn't matter.

The name you give your transitions does: this is what links a Tina transition to a FlexFact event. The way this has been defined is that the name of a transition should match the name of the FlexFact event (details of which you can find on the FlexFact website). However, since Tina (and probably the formal definition of Petri nets) don't permit duplicate transition names, anything after the character "X" in a transition name (except ";" - more details later) is ignores. This means you can call your transitions `sf_fdon`, `sf_fdonX` and `sf_fdonXsomereallylongsentence` and they will all be treated as `sf_fdon` when sending an event to FlexFact.

The ";" character at the start of a name ignores that transition, allowing tokens to pass freely. This is helpful when using a transition to explain something.

When used in the middle of a name, ";" separates the name into component parts, so you can use, for example, `sf_fdon;cb1_bm+` to trigger the `sf_fdon` and `cb1_bm+` events. Be warned that this hasn't been well tested.

## How to export your Petri nets

Click on Edit->Textify. The resulting output can be save in a `.net` file.

## Running the controller

Install the dependencies with `pip install requirements.txt`, or simply install pyModbusTCP with `pip install pyModbusTCP`.

Start the simulation in FlexFact and run the controller with `python controller.py`, or use `python controller.py -h` for more info.

## Limitations

Because this is basically a loop running every 10ms (or whatever you use), it can cause the simulator to slow a little. There may be a more efficient way of implementing this, but it would require significant reworking of the idea.

Since Modbus involves checking the values of an input, this system initially works with values, rather than transitions. This is fixed by using the checkTransition function.

## License

This project was developed as part of a module project at the Universidade Federal do Rio Grande do Sul and is licensed under the MIT license.
