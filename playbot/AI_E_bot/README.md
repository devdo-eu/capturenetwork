## Neural Network Bot
Inside this folder is bot powered by narrow AI.

`network.json` file contains network architecture details such as number of layers,
 number of neurons in a given layer, layer type, type of activation function, presence of bias and others.
 
`network.md5` file contains all weight for network from json-file.
 
 ### Network Architecture Details
```
_________________________________________________________________
Layer (type)                 Output Shape              Param #
=================================================================
dense_21 (InputLayer)        [(None, 108)]             0
_________________________________________________________________
dense_22 (Dense)             (None, 54)                5886
_________________________________________________________________
dense_23 (Dense)             (None, 54)                2970
_________________________________________________________________
dense_24 (Dense)             (None, 7)                 385
=================================================================
Total params: 9,241
Trainable params: 9,241
Non-trainable params: 0
```
 Neural network of this bot has 4 layers: input(Dense), hidden(Dense), hidden(Dense), output(Dense)
 
 As you can see, all layers are basic `Dense` type.
 
 Input layer has 108 neurons.
 
 Both hidden layers has 54 neurons
 
 Output layer has 7 neurons (one for each move available in game)
 
 So it looks like this: 108 -> 54 -> 54 -> 7
 
 First 3 layers has activation function `sigmoid` and last layer has activation function set to `linear`
 
 It is using float32 variables as weights.
 
 This network use 9241 weights.
 
 ### How it was trained?
 This model was trained in unsupervised reinforced fashion. 
 
 What dose it mean? It means that network was learning the game itself by playing
 
 ### Closing word
 If you had some question - let me know - and I will try to answer.